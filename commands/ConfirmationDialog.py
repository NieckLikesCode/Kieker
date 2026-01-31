import discord

from utils import localization


class ConfirmationDialog(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None
        self.original_interaction = interaction
        self.locale = interaction.locale

        # Update button text
        yes_button = self.children[0]
        yes_button.label = localization.translator.get('confirmationDialog.buttonYes', locale=interaction.locale)

        no_button = self.children[1]
        no_button.label = localization.translator.get('confirmationDialog.buttonNo', locale=interaction.locale)

    @discord.ui.button(
        label='Yes',
        style=discord.ButtonStyle.green,
        emoji='✅'
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            return

        self.value = True
        for child in self.children: child.disabled = True

        await interaction.response.edit_message(view=None)
        self.stop()

    @discord.ui.button(
        label='No',
        style=discord.ButtonStyle.red,
        emoji='❌'
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.original_interaction.user.id:
            return

        self.value = False
        for child in self.children: child.disabled = True

        await interaction.response.edit_message(view=None)
        self.stop()

    async def on_timeout(self):
        message = localization.translator.get('confirmationDialog.timeout', locale=self.locale)
        if self.value is None:

            for child in self.children: child.disabled = True
            await self.original_interaction.edit_original_response(content=message, view=None)