# Discord integration
token = '' # Your bots secret Discord token
monitored_channels = [] # channels you want to monitor
archive_message = '# {title} - {game}\n> was posted {timestamp} by [{author_name}]({author_url}).\n> Watch on [Medal.tv]({url})'
archive_channel_id = 123456789 # channel you want to send archived clips to

# Clip downloader
download_message = '# {title} - {game}\n> by [{author_name}]({author_url}).\n> Watch on [Medal.tv]({url})'
upload_notice = "The clip you want to download no longer appears to be stored on the Medal servers. However, it still exists in my database, from where I can upload it to an external file hosting provider ([Litterbox](https://litterbox.catbox.moe/)). The file would then be accessible for 1 hour and deleted afterwards. In the meantime, however, anyone who has the download link or guesses it can access the file. Would you still like me to upload the file for you?"
timeout_message = "You waited too long to respond, so the upload will be canceled. If you change your mind, please run the command again. "
button_upload_yes = "Yes"
button_upload_no = "No"
upload_aborted = "Upload aborted :sleeping:"
upload_confirmation = "Scheduled clip for upload. The link should be ready shortly :mechanic:"

# Clips
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
verbose = False