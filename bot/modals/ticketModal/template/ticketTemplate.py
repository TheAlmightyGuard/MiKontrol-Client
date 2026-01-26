from typing import List
import discord, os
from datetime import datetime

from models.tickets import TicketModalTemplate, TicketModalSelectOption

from services.ticket_services import ticket_create, ticket_assign


class TicketModalView(discord.ui.View):
    def __init__(self, modal = None):
        self.modal = modal
        self.error = None
        super().__init__(timeout=None)

    @discord.ui.button(label="💼 Take the case", style=discord.ButtonStyle.grey, custom_id="persistent:mod_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        modId = int(os.getenv("MOD_ROLE"))
        if not (interaction.user.get_role(modId) or interaction.user.guild_permissions.kick_members):
            await interaction.response.send_message(
                content="You don't have permissions to accept tickets!",
                ephemeral=True,
                delete_after=10
            )
            return


        embed = interaction.message.embeds[0]
        embed = embed.copy()

        violatorId = 0
        reporterId = 0

        for field in embed.fields:
            if field.name == "Offender":
                violatorId = int(field.value[2:-1])

            elif field.name == "Reporter":
                reporterId = int(field.value[2:-1])


        if (interaction.user.id == violatorId) or (interaction.user.id == reporterId):

            self.error = await interaction.response.send_message(
                content="You cannot accept to moderate a ticket against you / you created yourself!",
                delete_after=10,
                ephemeral=True
            )
            return

        
        embed.add_field(
            name="Assigned Moderator:",
            value=f"{interaction.user.mention}",
            inline=False
        )

        button.disabled = True
        button.label = "Taken by Moderator"

        await ticket_assign(self.modal.id, interaction.user.id)

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class TicketModal(discord.ui.Modal):

    def __init__(self, template : TicketModalTemplate):
        super().__init__(title=template.title)
        self.template = template

        for field in self.template.fields:
            item = getattr(discord.ui, field.component)
            
            component = None

            if field.component == "TextInput":
                component = discord.ui.Label(
                    text=field.title,
                    description=field.description,
                    component=item(
                        style=getattr(discord.TextStyle, field.textStyle),
                        required=field.required,
                        max_length=field.max_length
                    )
                )
            elif field.component != "Select":
                component = discord.ui.Label(
                    text=field.title,
                    description=field.description,
                    component=item(
                        required=field.required
                    )
                )
            elif field.component == "Select":

                options : List[discord.SelectOption] = []

                if field.selectOptions is None:
                    pass

                for option in field.selectOptions:
                    if isinstance(option, TicketModalSelectOption):
                        options.append(
                            discord.SelectOption(
                                label=option.title,
                                value=option.value if option.value is not None else option.title,
                                description=option.description
                            )
                        )

                component = discord.ui.Label(
                    text=field.title,
                    description=field.description,
                    component=item(
                        required=field.required,
                        options=options
                    )
                )

            self.add_item(component)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("heh")
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
