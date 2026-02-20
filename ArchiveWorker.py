import asyncio
import logging
import os
from dataclasses import dataclass

import discord

import config
from Clip import Clip
from DiscordBot import DiscordBot
from utils import video_utils, localization


@dataclass
class Entry:
    clip: Clip
    file_path: str

logger = logging.getLogger(__name__)


class ArchiveWorker:
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    async def start(self):
        """
        Starts the ArchiveWorker
        """
        await self.bot.wait_until_ready()

        while True:
            archive_entry = await self.bot.upload_queue.get()

            clip = archive_entry.clip
            file_path = archive_entry.file_path

            if config.verbose:
                logger.info(f'Initiating archiving process of {clip.title}')

            message = localization.translator.get(
                key='archive.message',
                locale=config.default_locale,
                title=clip.title,
                author_name=clip.author.name,
                author_url=clip.author.link,
                game=clip.game,
                time=clip.time,
                url=clip.url,
                timestamp=clip.timestamp(),
            )

            archive_channel = self.bot.get_channel(config.archive_channel_id)
            attachment_path = None

            file_size = os.path.getsize(file_path)
            maximum_file_size = archive_channel.guild.filesize_limit

            if file_size <= maximum_file_size: # No compression necessary,
                attachment_path = file_path

                if config.verbose:
                    logger.info(f'{clip.title} is small enough already! Skipping compression.')

            elif config.enable_compression: # File exceeds limit and compression is enabled
                if config.verbose:
                    logger.info(f'Initiating compression of {clip.title}')

                compressed_path = await asyncio.to_thread(
                    video_utils.compress_video,
                    video_full_path=file_path,
                    size_upper_bound=maximum_file_size/1024)

                if compressed_path is False:
                    logger.fatal('Error compressing video! (Have you installed FFMPEG correctly?)')
                    exit(1)

                logger.info(f'Successfully compressed {clip.title} to {compressed_path}')

                attachment_path = compressed_path

            attachment = None

            if attachment_path is not None:
                attachment = discord.File(attachment_path)
            else:
                message += '\n-# '+localization.translator.get('archive.fileTooBig', locale=config.default_locale)

            archive_channel = self.bot.get_channel(config.archive_channel_id)
            await archive_channel.send(content=message, file=attachment, suppress_embeds=True)

            if attachment_path is not None and attachment_path is not file_path: # Compression took place
                if config.keep_compressed_files:
                    os.remove(file_path)
                    os.rename(attachment_path, file_path)
                else:
                    os.remove(attachment_path)

            await asyncio.to_thread(
                self.bot.database.update_status,
                url=clip.url,
                status="ARCHIVED"
            )

            self.bot.upload_queue.task_done()
            self.bot.queued_links.remove(clip.url)

