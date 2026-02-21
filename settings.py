import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_TOKEN")

# Archive
monitored_channels = [
        int(channel_id.strip())
        for channel_id in os.getenv('MONITORED_CHANNEL_IDS').split(",")
        if channel_id.strip()
    ]

archive_channel_id = int(os.getenv("ARCHIVE_CHANNEL_ID"))

# Localization
enable_localization = True if os.getenv("ENABLE_LOCALIZATION").upper() == 'True' else False
default_locale = os.getenv("DEFAULT_LOCALE")

# Download settings
download_path = os.getenv("DOWNLOAD_PATH")
naming_scheme = os.getenv("FILE_NAMING_SCHEME")

# Compression
enable_compression = True if os.getenv("ENABLE_COMPRESSION").upper() == 'True' else False
keep_compressed_files = True if os.getenv("KEEP_COMPRESSED_FILES").upper() == 'True' else False

maximum_video_width = int(os.getenv("MAXIMUM_VIDEO_WIDTH"))
maximum_threads = int(os.getenv("MAXIMUM_THREADS"))

# Database
database_path = os.getenv("DATABASE_PATH")

# Logging
disable_logging = True if os.getenv("DISABLE_LOGGING").upper() == 'False' else False
log_directory = os.getenv("LOG_DIRECTORY")
verbose = True if os.getenv("VERBOSE_LOGGING").upper() == 'True' else False