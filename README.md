# 💾 Kieker
Kieker is a discord bot that helps you download and archive your [Medal.tv](https://medal.tv/) clips.

## 🎛 Features
Archiving clips works by:
1. Scanning an existing channel for links and listening for new messages with clips.
2. Downloading them without a watermark and storing their metadata and file location in a database. 
3. Posting archived clips to (another) Discord channel.

### On uploading local copies and compression
By default, Kieker will also try to attach its local copies of clips to the archive messages to create a mirror 
and make them accessible to all your friends.

**If the clip exceeds Discords file size limit (10 MB), it will be skipped by default.** To circumvent this restriction
the bot can be configured to compress the clip using [FFMPEG](https://www.ffmpeg.org/). Thanks to [ESWZY](https://github.com/ESWZY) the
amount of compression will be chosen just high enough to fit within the limit. If the quality of the source video
exceeds a certain maximum (1080p by default) it will be resized before compression to improve video quality.

**Video compression is very expensive and will max out your CPU**. If you don't want this you can set the amount of
threads that will be used for compression in the config. Rule of thumb for overwhelmed users: the total amount of usable
threads is twice your CPU core count. If you allocate half of the total available threads to compression then your
CPU will use about 50% of its power to compress the video (e.g. 4 cores → 8 threads, so 4 threads will cause 
50% usage).

## 🔒 Limitations

#### Metadata
Kieker retrieves its metadata and local copies by scraping the clips webpage. To optimize resource usage scraping is 
done without using any kind of headless browser. Instead, it simply parses the GET request and extracts information from
there. This works well as most of the metadata is already nicely encoded in a JSON object contained in an embedded
script. The only metadata that does not have its own entry in the JSON is the game from which the clip originates. 
Fortunately, however, the game always seems to be the word of the "keywords" value, so this is used as a workaround.
I don't want to rule out the possibility that this method may fail with older clips, for example, and that
 - the game may not be recognized at all
 - incorrect information will be read
 - formatting of the games name will be messed up

If you encounter this issue, feel free to open an issue on it, maybe we can work something out together. 

#### Deleted/Missing clips
In theory uploaded clips are supposed to be stored on their servers indefinitely unless you delete them yourself. In
reality old links seem to be getting inaccessible rather regularly which only reinforces the urge to back up clips.
**If a link becomes inaccessible it's impossible for the bot to download.
Kieker to recover any data**. If the bot detects a deleted video it 
marks it as 'DELETED' in the database. You might be able to recover clips by following [this](https://support.medal.tv/support/solutions/articles/48001258056-restoring-deleted-videos)
written guide. Although you can specify deleted or missing clips as a category in a support ticket, there is little 
the platform can do, so I would advise against contacting them as not to use up their capacity unnecessarily.
**If you decide to do so anyway, please keep in mind that Kieker is in no way affiliated with Medal.**

Since I have never managed to recover clips myself, I don't know how to cover this case. You may always
remove all invalid links from the database by using "**/remove_invalid**" and then forcing a rescan by restarting the 
program.

#### Quality
To prevent watermarks on videos, videos will be downloaded via the “content-url,” which is also used for (Discord) 
embeds. For some reason the quality of the embedded videos can vary. This might cause a clip that was uploaded in 1080p
to only produce a 720p copy. If you know how to bypass this feel free to open an issue.

## 🔧 Installation
1. Clone this repository `git clone https://github.com/NieckLikesCode/Kieker`
2. Install all the requirements `pip install -r requirements.txt`
3. [Create a discord bot account](https://discordpy.readthedocs.io/en/stable/discord.html) and copy your token. Make sure to give the bot permissions to read and write
messages
4. Create your configuration by renaming `example_config.py` to `config.py` and configuring the variables in it. A 
minimal configuration requires setting `token ` and `monitored_channels`
5. If you wanna use video compression make sure to install `ffmpeg`. [See also](https://github.com/kkroening/ffmpeg-python/issues/251) 
6. Run the bot `python discord-bot.py`

## 💌 Thank yous
 - [Django](https://github.com/django/django) for their ["slugify"](https://github.com/django/django/blob/3923ebac28672ef4ebfbf2685fbc93206e6c136e/django/utils/text.py#L468C16-L469C5) 
 function to create legal file names
 - [ESWZY](https://github.com/ESWZY) code for [compressing videos to a target size](https://gist.github.com/ESWZY/a420a308d3118f21274a0bc3a6feb1ff)