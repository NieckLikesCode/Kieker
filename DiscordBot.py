import asyncio
import logging
import os
from time import strftime, gmtime

import discord
from discord.ext import commands, tasks

import ArchiveWorker
import DownloadWorker
import config
from Database import Database
from utils.text_utils import find_link_in_message, sanitize_link


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix='!')

        self.database = Database(config.database_path)
        self.download_queue = asyncio.Queue()
        self.upload_queue = asyncio.Queue()
        self.queued_links = set()

        self.download_worker = None
        self.archive_worker = None


    async def on_ready(self):
        logging.info(f'Logged in as {self.user} (ID: {self.user.id})')


    async def setup_hook(self):
        self.download_worker = DownloadWorker.DownloadWorker(bot=self)
        self.archive_worker = ArchiveWorker.ArchiveWorker(bot=self)

        # Start tasks
        self.loop.create_task(self.scan_channel_history())
        self.loop.create_task(self.download_worker.start())
        self.loop.create_task(self.archive_worker.start())

        # Update activity periodically
        self.update_activity.start()

        # Load commands
        await self.load_extension('commands.RemoveInvalid')
        await self.load_extension('commands.DownloadClip')

        await self.tree.sync()


    async def on_message(self, message: discord.Message):

        if message.channel.id not in config.monitored_channels:
            return

        if message.author == self.user:
            return

        link = find_link_in_message(message.content)

        if link is None:
            return

        logging.info(f'{message.author.name} shared clip: {link}')
        await self.handle_link(link)


    async def scan_channel_history(self):
        await self.wait_until_ready()

        for channel_id in config.monitored_channels:
            channel = self.get_channel(channel_id)

            if not channel:
                logging.error(f'Unable to find channel with id {channel_id}')
                continue

            messages = channel.history(limit=None, oldest_first=True)

            async for message in messages:
                await asyncio.sleep(0)

                if message.author == self.user:
                    continue

                text = message.content

                if 'medal.tv' not in text:
                    continue

                link = sanitize_link(
                    find_link_in_message(text)
                )

                await self.handle_link(link)


    async def handle_link(self, link: str):
        """
        Either skips the link if it's invalid, puts it into the download queue if not already downloaded or sends it
        to the archive queue if it's already been dowloaded but never posted
        :param link: clip link
        """

        if link in self.queued_links:
            return

        status = self.database.get_status(link)

        if status == 'ARCHIVED':
            return
        else:
            self.queued_links.add(link)

            if status == 'DOWNLOADED':
                clip = self.database.get_clip_from_url(link)
                file_path = self.database.get_file_path(link)

                logging.info(f'{clip.title} is already downloaded! Sending video to archive.')

                await self.upload_queue.put(ArchiveWorker.Entry(clip, file_path))
            else:
                await self.download_queue.put(link)


    @tasks.loop(seconds=10)
    async def update_activity(self):
        amount_to_download = self.download_queue.qsize()
        amount_to_upload = self.upload_queue.qsize()

        archived_count = self.database.get_archived_count()

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f'{archived_count} clips archived',
            state=f'{amount_to_download} pending downloads, {amount_to_upload} clips waiting to be uploaded.'
        )

        await self.change_presence(activity=activity)

    @update_activity.before_loop
    async def before_update_activity(self):
        await self.wait_until_ready()


if __name__ == "__main__":
    # Create log directory
    if not os.path.isdir(config.log_directory):
        os.mkdir(config.log_directory)

    # Create download directory
    if not os.path.isdir(config.download_path):
        os.mkdir(config.download_path)

    logging.basicConfig(
        level=logging.INFO,
        filename=f'{config.log_directory}/{strftime("%Y-%m-%d at %H %M %S", gmtime())}.log',
        filemode='a',
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

    if not config.disable_logging:
        discord.utils.setup_logging(level=logging.INFO, root=False)

    bot = DiscordBot()
    bot.run(config.token, log_handler=None)

