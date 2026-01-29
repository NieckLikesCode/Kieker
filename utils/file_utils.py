import os

import aiofiles
import aiohttp

API_URL = 'https://litterbox.catbox.moe/resources/internals/api.php'

async def upload_file(file_path: str):
    '''
    Uploads the specified file asynchronously to Litterbox
    :param file_path: path to the file to upload
    :return: Download link if successful, otherwise None
    '''
    if os.path.getsize(file_path) > pow(10, 9):
        raise ValueError('File size exceeds 1 GB')

    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            data = {'reqtype': 'fileupload', 'time': '1h', 'fileToUpload': file}

            async with session.post(API_URL, data=data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None

async def download_asynchronous(url: str, path: str):
    """
    Download file from url asynchronously
    :param url: url to file
    :param path: target path
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async with aiofiles.open(path, mode='wb') as f:
                async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB Chunks
                    await f.write(chunk)