import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

import settings
from Clip import Clip
from DiscordBot import DiscordBot
from commands.ConfirmationDialog import ConfirmationDialog
from utils import localization
from utils.file_utils import upload_file
from utils.text_utils import sanitize_link, find_link_in_message

async def setup(bot):
    await bot.add_cog(DownloadClip(bot))

class DownloadClip(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Download Clip",
            callback=self.context_download_callback,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def _process_download(self, interaction: discord.Interaction, link: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        clip_link = find_link_in_message(link)

        if clip_link is None:
            await interaction.followup.send("Request doesnt contain a Medal.tv link.")
            return

        clip_link = sanitize_link(clip_link)

        clip = Clip.from_url(clip_link)
        status = self.bot.database.get_status(clip_link)

        if clip is not None:
            await interaction.followup.send(f'[Download here]({clip.content_url})', ephemeral=True)
        elif status == 'DOWNLOADED' or status == 'ARCHIVED':
            clip_location = self.bot.database.get_file_path(clip_link)
            file_size = os.path.getsize(clip_location)

            if file_size <= interaction.guild.filesize_limit:  # File can be uploaded as message attachment
                discord_file = discord.File(clip_location)
                await interaction.followup.send(file=discord_file, ephemeral=True)
            else:  # Upload file to Litterbox

                confirmation_dialog = ConfirmationDialog(interaction)
                confirmation_message = localization.translator.get(
                    'downloadRequest.uploadConfirmation',
                    locale=interaction.locale
                )

                await interaction.followup.send(
                    content=confirmation_message,
                    view=confirmation_dialog,
                    ephemeral=True
                )

                await confirmation_dialog.wait()

                if confirmation_dialog.value is True:
                    logging.info(f'Uploading {clip_link} to Litterbox')

                    working_message = localization.translator.get(
                        'downloadRequest.queueNotification',
                        locale=interaction.locale
                    )

                    await interaction.edit_original_response(content=working_message)

                    clip_location = self.bot.database.get_file_path(clip_link)
                    download_link = await upload_file(clip_location)

                    message = None

                    if download_link is None:
                        message = localization.translator.get('downloadRequest.uploadFailed', locale=interaction.locale)
                    else:
                        message = f'[Download here]({download_link})'

                    if settings.verbose:
                        if download_link is not None:
                            logging.info(f'Successfully uploaded video: {download_link}')
                        else:
                            logging.warning(f'Failed to upload video: {clip_link}')

                    await interaction.edit_original_response(content=message)
                else:
                    abort_message = localization.translator.get('downloadRequest.uploadAborted', locale=interaction.locale)
                    await interaction.edit_original_response(content=abort_message)

        else:
            await interaction.followup.send(
                content=localization.translator.get('downloadRequest.clipInaccessible', locale=interaction.locale),
                ephemeral=True
            )

    @app_commands.describe(link='Link to the clip you want to download')
    @app_commands.command(name='download', description='Provides a download link for the specified clip')
    async def download_command(self, interaction: discord.Interaction, link: str):
        await self._process_download(interaction, link)

    async def context_download_callback(self, interaction: discord.Interaction, message: discord.Message):
        await self._process_download(interaction, message.content)

