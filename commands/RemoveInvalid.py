import discord
from discord import app_commands
from discord.ext import commands

from DiscordBot import DiscordBot

async def setup(bot):
    await bot.add_cog(RemoveInvalid(bot))

class RemoveInvalid(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @app_commands.command(name='remove_invalid', description='Remove invalid clips from database')
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_invalid(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        deleted_count = self.bot.database.delete_invalid_rows()

        if deleted_count == 0:
            await interaction.followup.send(
                'No invalid clips sniffed out :mouse2:',
                ephemeral=True)
        else:
            s_suffix = 's' if deleted_count > 1 else ''
            await interaction.followup.send(
                f'Deleted **{deleted_count}** invalid clip{s_suffix} from the database :wastebasket:',
                ephemeral=True
            )