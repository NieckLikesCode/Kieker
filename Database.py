import sqlite3
import logging

import config
from Clip import Clip
from Clip import Uploader

# Setup logging
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, name):
        self.name = name
        self.connection = None
        self._create_table()

    def _connect(self):
        """
        Establishes connection with the database
        """
        if not self.connection:
            self.connection = sqlite3.connect(self.name, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row

    def _create_table(self):
        """
        Tries to create the table in the database. If it already exists no changes will be made.
        """
        self._connect()
        query = '''CREATE TABLE IF NOT EXISTS clips (
            url TEXT PRIMARY KEY,
            status TEXT,
            title TEXT,
            author_name TEXT,
            author_link TEXT,
            game TEXT,
            file_path TEXT,       
            datetime TEXT)'''
        self.connection.execute(query)
        self.connection.commit()

    def clip_exists(self, url):
        """
        Checks whether a url exists in the database
        :param url: url of clip to check
        :return: True if clip exists, else False
        """
        cursor = self.connection.execute('SELECT 1 FROM clips WHERE url = ?', (url,))
        exists_in_database = cursor.fetchone() is not None
        return exists_in_database

    def add_clip(self, clip: Clip, location: str, status: str):
        """
        Adds a clip to the database
        :param clip: clip to add
        :param location: file location of the clip
        :param status: clips archiving status
        :return: True if adding was successful, else False
        """
        try:

            query = '''
            INSERT INTO clips (url, status, title, author_name, author_link, game, file_path, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''

            self.connection.execute(query, (
                clip.url,
                status,
                clip.title,
                clip.author.name,
                clip.author.link,
                clip.game,
                location,
                clip.time
            ))
            self.connection.commit()
            logger.info(f'Successfully wrote {clip.title} ({clip.url}) to database')
            return True

        except sqlite3.IntegrityError:
            logger.warning(f'Skipped duplicate clip "{clip.title}" ({clip.url})')
            return False

    def add_invalid_link(self, url):
        """
        Adds an invalid link to the database
        :param: url: invalid url
        :return: True if adding was successful, else False
        """
        try:

            query = '''
            INSERT INTO clips (url, status, title, author_name, author_link, game, file_path, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''

            self.connection.execute(query, (url, 'INVALID', '', '', '', '', '', ''))
            self.connection.commit()

            if config.verbose:
                logger.info(f'Successfully wrote invalid link {url}')
            return True

        except sqlite3.IntegrityError:
            logger.warning(f'Invalid link {url} already exists! Skipping.')
            return False

    def update_status(self, url, status):
        """
        Updates the status of an existing clip
        :param url: url of clip to update
        :param status: new status
        """
        self.connection.execute( 'UPDATE clips SET status = ? WHERE url = ?', (status, url))
        self.connection.commit()

    def get_status(self, url):
        """
        Reads the clip status from the database
        :param url: url of clip to read
        :return: status of the clip, None is clip doesn't exist
        """
        cursor = self.connection.execute('SELECT status FROM clips WHERE url = ?', (url,))
        row = cursor.fetchone()

        return row['status'] if row else None

    def get_file_path(self, url):
        """
        Reads the clip status from the database
        :param url: url of clip to read
        :return: file path of clip
        """
        cursor = self.connection.execute('SELECT file_path FROM clips WHERE url = ?', (url,))
        row = cursor.fetchone()
        return row['file_path']

    def get_clip_from_url(self, url):
        """
        Reconstructs a clip from the database
        :param url: url of clip to read
        :return: corresponding clip object
        """
        query = 'SELECT * FROM clips WHERE url = ?'
        cursor = self.connection.execute(query, (url,))
        row = cursor.fetchone()

        author = Uploader(row['author_name'], row['author_link'])

        clip = Clip(
            url=row['url'],
            title=row['title'],
            author=author,
            game=row['game'],
            time=row['datetime'],
            content_url=None
        )

        return clip

    def delete_invalid_rows(self):
        """
        Deletes all invalid rows from the database
        :return: amount of deleted rows
        """
        query = 'DELETE FROM clips WHERE status = ?'
        cursor = self.connection.execute(query, ('INVALID',))
        self.connection.commit()

        return cursor.rowcount

    def get_archived_count(self):
        """
        Returns the amount of clips stored in the database as ARCHIVED
        :return: amount of rows in the database
        """
        query = 'SELECT COUNT(*) FROM clips WHERE status = ?'
        cursor = self.connection.execute(query, ('ARCHIVED',))

        result = cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        if self.connection:
            self.connection.close()
