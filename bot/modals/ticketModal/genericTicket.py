import discord
from datetime import datetime

from bot.modals.ticketModal.samples.moderation import ModerationModal

class GeneralModal(discord.ui.Modal, title="Open a ticket [ ??? ]"):

    type = discord.ui.Label(
        text='Report Type',
        description='Select the type of the report.',
        component=discord.ui.Select(
            placeholder='Choose a type...',
            options=[
                discord.SelectOption(label='Moderation', description='Report will be directed to Moderation Team'),
                discord.SelectOption(label='Development', description='Report will be directed to Developer Team Support')
            ],
        ),
    )

    async def on_submit(self, interaction: discord.Interaction):

        # Standard check for your select menu
        assert isinstance(self.type.component, discord.ui.Select)
        target = self.type.component.values[0]

        modal = None

        if target == "Moderation":
            modal = ModerationModal()
        elif target == "Developer":
            modal = None

        if modal is None:
            raise Exception

        view = discord.ui.View()

        embed = discord.Embed(
            title="Ticket System",
        )

        embed.add_field(
            name="You have selected to open a Moderation Ticket...",
            value="Click to continue or cancel ticket."
        )

        embed.set_footer(
            text="Auto-cancel in 10 seconds..."
        )

        continue_btn = discord.ui.Button(
            label="Continue",
            style=discord.ButtonStyle.green
        )

        async def continue_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(modal)
            await interaction.message.delete()

        continue_btn.callback = continue_callback

        exit_btn = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.red
        )

        async def exit_callback(interaction: discord.Interaction):
            await interaction.message.delete()
            return

        exit_btn.callback = exit_callback

        view.add_item(continue_btn)
        view.add_item(exit_btn)

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
            delete_after=10
        )
        self.stop()
        
            

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
