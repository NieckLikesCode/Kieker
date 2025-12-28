import discord
import logging
import os

from discord import app_commands
from discord.ext import tasks

import config
import asyncio

from ArchiveWorker import ArchiveWorker, Entry
from Database import Database
from time import gmtime, strftime
from DownloadWorker import DownloadWorker
from utils.text_utils import find_link_in_message, sanitize_link

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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

database = Database(config.database_path)

download_queue = asyncio.Queue()
upload_queue = asyncio.Queue()

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

    await tree.sync()

    if not update_activity.is_running():
        update_activity.start()


@client.event
async def setup_hook():
    download_worker = DownloadWorker(download_queue=download_queue,
                                     upload_queue=upload_queue,
                                     download_path=config.download_path,
                                     database=database,
                                     bot=client,
                                     verbose=config.verbose)

    archive_worker = ArchiveWorker(upload_queue=upload_queue,
                                   database=database,
                                   bot=client,
                                   verbose=config.verbose)

    asyncio.create_task(scan_channel_history())
    asyncio.create_task(download_worker.start())
    asyncio.create_task(archive_worker.start())


@client.event
async def on_message(message):

    if message.channel.id not in config.monitored_channels:
        return

    if message.author == client.user:
        return

    link = find_link_in_message(message.content)

    if link is None:
        return

    logging.info(f'{message.author.name} shared clip: {link}')
    await download_queue.put(link)

async def scan_channel_history():
    await client.wait_until_ready()

    for channel_id in config.monitored_channels:
        channel = client.get_channel(channel_id)

        if not channel:
            logging.error(f'Unable to find channel with id {channel_id}')
            continue

        messages = channel.history(limit=None, oldest_first=True)

        async for message in messages:
            await asyncio.sleep(0)

            if message.author == client.user:
                continue

            text = message.content

            if 'medal.tv' not in text:
                continue

            link = sanitize_link(
                find_link_in_message(text)
            )

            if not database.clip_exists(link):
                await download_queue.put(link)
            elif database.get_status(link) == 'DOWNLOADED':
                clip = database.get_clip_from_url(link)
                file_path = database.get_file_path(link)

                logging.info(f'{clip.title} is already downloaded! Sending video to archive.')

                await upload_queue.put(Entry(clip, file_path))

if not config.disable_logging:
    discord.utils.setup_logging(level=logging.INFO, root=False)
    pass

@tree.command(name="remove_invalid", description="Deletes all invalid links from the database.")
async def remove_invalid(interaction: discord.Interaction):
    deleted_count = database.delete_invalid_rows()

    if deleted_count == 0:
        await interaction.response.send_message('No invalid clips sniffed out :mouse2:', ephemeral=True)
    else:
        await (interaction.response.send_message(
            f'Deleted **{deleted_count}** invalid clip{'s' if deleted_count > 1 else ''} from the database :wastebasket:'))

@tasks.loop(seconds=10)
async def update_activity():

    amount_to_download = download_queue.qsize()
    amount_to_upload = upload_queue.qsize()

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f'{database.get_archived_count()} clips archived',
        state=f'{amount_to_download} pending downloads, {amount_to_upload} clips waiting to be uploaded.'
    )

    await client.change_presence(activity=activity)

client.run(config.token, log_handler=None)