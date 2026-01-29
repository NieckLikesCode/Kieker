import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

import config
from Clip import Clip
from DiscordBot import DiscordBot
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
            await interaction.followup.send(f'[Download link]({clip.content_url})', ephemeral=True)
        elif status == 'DOWNLOADED' or status == 'ARCHIVED':
            clip_location = self.bot.database.get_file_path(clip_link)
            file_size = os.path.getsize(clip_location)

            if file_size <= interaction.guild.filesize_limit:  # File can be uploaded as message attachment
                discord_file = discord.File(clip_location)
                await interaction.followup.send(file=discord_file, ephemeral=True)
            else:  # Upload file to Litterbox

                if config.verbose:
                    logging.info(f'Uploading {clip_link} to Litterbox...')

                confirmation = ConfirmUploadView(interaction)

                await interaction.followup.send(
                    content=config.upload_notice,
                    view=confirmation,
                    ephemeral=True
                )

                await confirmation.wait()
                if confirmation.value is True:
                    clip_location = self.bot.database.get_file_path(clip_link)
                    download_link = await upload_file(clip_location)
                    message = f'[Download link]({download_link})' if download_link is not None else ':x: Unable to upload clip. Please try again later or contact the bot maintainer.'

                    await interaction.edit_original_response(content=message)
        else:
            await interaction.followup.send(
                'Unfortunately, the specified clip cannot be found directly on the Medal Server, nor is it backed up in the database. :melting_face:',
                ephemeral=True)

    @app_commands.describe(link='Link to the clip you want to download')
    @app_commands.command(name='download', description='Provides a download link for the specified clip')
    async def download_command(self, interaction: discord.Interaction, link: str):
        await self._process_download(interaction, link)

    async def context_download_callback(self, interaction: discord.Interaction, message: discord.Message):
        await self._process_download(interaction, message.content)

class ConfirmUploadView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None
        self.original_interaction = interaction

    @discord.ui.button(label=config.button_upload_yes, style=discord.ButtonStyle.green, emoji='✅')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            return

        self.value = True
        for child in self.children: child.disabled = True

        await interaction.response.edit_message(content=config.upload_confirmation, view=None)
        self.stop()

    @discord.ui.button(label=config.button_upload_no, style=discord.ButtonStyle.red, emoji='❌')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            return

        self.value = False
        for child in self.children: child.disabled = True

        await interaction.response.edit_message(content=config.upload_aborted, view=None)
        self.stop()

    async def on_timeout(self):
        if self.value is None:

            for child in self.children: child.disabled = True
            await self.original_interaction.edit_original_response(content=config.timeout_message, view=None)