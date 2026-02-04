from typing import List
import discord

from datetime import datetime

from bot.modals.ticketModal.samples.modals.moderation import ModerationModal
from bot.modals.ticketModal.samples.modals.developer import DeveloperModal

from models.tickets import TicketModalTemplate
from models.guild import GuildPreferences

from bot.modals.ticketModal.template.ticketTemplate import TicketModal
from utils.time_functions import add_time
class GeneralModal(discord.ui.Modal, title="Open a ticket [ ??? ]"):

    def __init__(self, guildConfig : GuildPreferences):
        super().__init__()
        self.config = guildConfig

        options : List[discord.SelectOption] = []
        options.append(discord.SelectOption(label='Moderation', description='Report will be directed to Moderation Team'))
        options.append(discord.SelectOption(label='Development', description='Report will be directed to Developer Team Support'))

        for modal in guildConfig.custom_tickets:
            if isinstance(modal, TicketModalTemplate):

                option = discord.SelectOption(
                    label=modal.title,
                    description=modal.description,
                    value=modal.title
                )

                options.append(option)

        self.add_item(
            discord.ui.Label(
                text='Report Type',
                description='Select the type of the report.',
                component=discord.ui.Select(
                    placeholder='Choose a type...',
                    options=options
                ),
            )
        )

    

    async def on_submit(self, interaction: discord.Interaction):

        # Standard check for your select menu
        label = self.children[0]
        assert isinstance(label, discord.ui.Label)
        assert isinstance(label.component, discord.ui.Select)

        target = label.component.values[0]

        modal = None

        if target == "Moderation":
            modal = ModerationModal()
        elif target == "Development":
            modal = DeveloperModal()
        else:
            for custom in self.config.custom_tickets:
                if custom.title == target:
                    modal = TicketModal(
                        template=custom,
                        agent_id=custom.agent_id,
                        category_id=self.config.ticket_category
                    )

        if modal is None:
            raise Exception

        view = discord.ui.View()

        embed = discord.Embed(
            title="Ticket System",
            description=f"Auto-cancel <t:{round(add_time("10s", datetime.now()).timestamp())}:R>"
        )

        embed.add_field(
            name=f"You have selected to open a {target} Ticket...",
            value="Click to continue or cancel ticket."
        )

        embed.set_footer(
            text="Powered by MiKontrol"
        )

        continue_btn = discord.ui.Button(
            label="Continue",
            style=discord.ButtonStyle.green
        )

        async def continue_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(modal)

        continue_btn.callback = continue_callback

        exit_btn = discord.ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.red
        )

        async def exit_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.delete_original_response()
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
