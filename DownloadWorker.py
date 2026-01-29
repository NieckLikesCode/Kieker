import asyncio
import logging
import time
import aiofiles
import aiohttp
import discord

import ArchiveWorker
import config
from Clip import Clip
from Database import Database
from utils import text_utils
from utils.file_utils import download_asynchronous

logger = logging.getLogger(__name__)

class DownloadWorker:
    def __init__(self, download_queue: asyncio.Queue,
                 upload_queue: asyncio.Queue,
                 download_path: str,
                 database: Database,
                 bot: discord.Client,
                 verbose: bool):
        self.download_queue = download_queue
        self.upload_queue = upload_queue
        self.download_path = download_path
        self.database = database
        self.bot = bot
        self.verbose = verbose

    async def start(self):
        """
        Starts the download worker
        """
        await self.bot.wait_until_ready()

        while True:
            url = await self.download_queue.get()

            if self.verbose:
                logger.info(f'Retrieving metadata from clip {url}')

            clip = Clip.from_url(url)
            await asyncio.sleep(0)

            if clip is None:
                logger.warning(f'Clip {url} is invalid. Skipping.')
                self.database.add_invalid_link(url)
                continue

            filename = text_utils.format_placeholder_by_clip(config.naming_scheme, clip)

            path = self.download_path + text_utils.slugify(filename) + '.mp4'

            if self.verbose:
                logger.info(f'Initiating download of {filename} from {clip.content_url}')

            start_time = time.time()

            await download_asynchronous(clip.content_url, path)

            logger.info(f'Completed download of {filename} in {round(time.time() - start_time)} seconds')
            self.database.add_clip(clip, path, "DOWNLOADED")

            # Send archived clip over to ArchiveWorker to start upload
            await self.upload_queue.put(ArchiveWorker.Entry(clip, path))

            self.download_queue.task_done()

