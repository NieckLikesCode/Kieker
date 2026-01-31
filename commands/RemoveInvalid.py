import discord
from discord import app_commands
from discord.ext import commands

from DiscordBot import DiscordBot
from commands.ConfirmationDialog import ConfirmationDialog
from utils import localization


async def setup(bot):
    await bot.add_cog(RemoveInvalid(bot))

class RemoveInvalid(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @app_commands.command(name='remove_invalid', description='Remove invalid clips from database')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_invalid(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)


        confirmation_dialog = ConfirmationDialog(interaction)
        confirmation_message = localization.translator.get(
            'removeInvalid.deletionConfirmation',
            locale=interaction.locale
        )

        await interaction.followup.send(
            content=confirmation_message,
            view=confirmation_dialog,
            ephemeral=True
        )

        await confirmation_dialog.wait()

        if confirmation_dialog.value is True:
            deleted_count = self.bot.database.delete_invalid_rows()

            if deleted_count == 0:
                response = localization.translator.get('removeInvalid.noEffect', locale=interaction.locale)
                await interaction.edit_original_response(
                    content=response,
                )
            else:
                response = localization.translator.get('removeInvalid.rowsEffected', locale=interaction.locale, count=deleted_count)
                await interaction.edit_original_response(
                    content=response,
                )
        else:
            response = localization.translator.get('removeInvalid.deletionCanceled', locale=interaction.locale)
            await interaction.delete_original_response()

