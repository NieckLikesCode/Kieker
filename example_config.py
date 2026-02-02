token = '' # Your bots secret token

# Archive
monitored_channels = [] # channels you want to monitor
archive_channel_id = 123456789 # channel you want to send archived clips to

# Localization
enable_localization = True # Whether to enable automatic localization or not
archive_locale = 'en' # Language that will be used for archive messages

# Download settings
download_path = './clips/'
naming_scheme = '{title} - {game} - {time}' # Removing time from the naming scheme will cause clips to be overwritten if their names are the same

# Compression
enable_compression = False
keep_compressed_files = False # Whether to replace the original clips with their compressed version
maximum_video_width = 1920 # height will be automatically chosen to keep aspect ratio of original video
maximum_threads = -1 # Set to -1 to disable throttling

# Database
database_path = 'archive.db'

# Logging
disable_logging = False
log_directory = './logs/'
verbose = True