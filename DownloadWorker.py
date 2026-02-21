import asyncio
import logging
import time

import ArchiveWorker
import settings
from Clip import Clip
import DiscordBot
from utils import text_utils
from utils.file_utils import download_asynchronous

logger = logging.getLogger(__name__)


class DownloadWorker:
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    async def start(self):
        """
        Starts the download worker
        """
        await self.bot.wait_until_ready()

        while True:
            url = await self.bot.download_queue.get()

            if settings.verbose:
                logger.info(f'Retrieving metadata from clip {url}')

            clip = Clip.from_url(url)
            await asyncio.sleep(0)

            if clip is None:
                logger.warning(f'Clip {url} is invalid. Skipping.')
                self.bot.database.add_invalid_link(url)
                continue

            filename = text_utils.format_placeholder_by_clip(settings.naming_scheme, clip)

            path = settings.download_path + text_utils.slugify(filename) + '.mp4'

            if settings.verbose:
                logger.info(f'Initiating download of {filename} from {clip.content_url}')

            start_time = time.time()

            await download_asynchronous(clip.content_url, path)

            logger.info(f'Completed download of {filename} in {round(time.time() - start_time)} seconds')
            self.bot.database.add_clip(clip, path, "DOWNLOADED")

            # Send archived clip over to ArchiveWorker to start upload
            await self.bot.upload_queue.put(ArchiveWorker.Entry(clip, path))

            self.bot.download_queue.task_done()

