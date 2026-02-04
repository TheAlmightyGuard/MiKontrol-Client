from typing import List
import discord
from datetime import datetime

from models.tickets import TicketModalTemplate, TicketModalSelectOption

from services.ticket_services import ticket_create, ticket_pull, ticket_close, ticket_assign
from utils.get_fetch import get_channel, get_role
from utils.time_functions import add_time

import asyncio
class TicketModalView(discord.ui.View):
    def __init__(self, modal = None, template : TicketModalTemplate = None):
        self.modal = modal
        self.template = template
        self.error = None
        super().__init__(timeout=None)

    @discord.ui.button(label="💼 Take the case", style=discord.ButtonStyle.grey, custom_id="req:case_accept")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        agentId = self.template.agent_id
        if not (interaction.user.get_role(agentId) or interaction.user.guild_permissions.kick_members):
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
            name="Assigned Agent:",
            value=f"{interaction.user.mention}",
            inline=False
        )

        button.disabled = True
        button.label = f"Taken by {interaction.user.name}"

        await ticket_assign(self.modal.id, interaction.user.id)

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(label="🎟️ Close Ticket", style=discord.ButtonStyle.red, custom_id="req:close_ticket")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel

        if channel is None:
            return
        
        agent = await ticket_pull(channel.name)
        authorized = False

        if agent == 0:
            if interaction.user.guild_permissions.administrator:
                authorized = True
            else:
                await interaction.response.send_message("You do not have permission to close unclaimed tickets!")
                return
        else:
            if agent == interaction.user.id:
                authorized = True
            else:
                await interaction.response.send_message("Unauthorized action. You are not the agent of this ticket.", delete_after=5, ephemeral=True)
                return


        if authorized:
            await ticket_close(channel.name, interaction.user.id, f"Agent {interaction.user.name} ({interaction.user.id}) has closed the ticket.")
            await interaction.response.send_message(f"Agent {interaction.user.name} ({interaction.user.id}) has closed this ticket. Closing <t:{round(add_time("5s", datetime.now()).timestamp())}:R>", delete_after=5, ephemeral=True)
            await asyncio.sleep(5)
            await interaction.channel.delete(reason=f"Agent {interaction.user.name} ({interaction.user.id}) has closed the ticket.")


class TicketModal(discord.ui.Modal):

    def __init__(self, template : TicketModalTemplate, agent_id : int, category_id : int):
        super().__init__(title=f"Open a Ticket [ {template.title} ]")
        self.template = template
        self.agent_id = agent_id
        self.category_id = category_id

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

        button = TicketModalView(self, self.template)

        category = await get_channel(interaction.guild, self.category_id)
        agent_ping = await get_role(interaction.guild, self.agent_id)

        if agent_ping is not None:
            text_channel = await interaction.guild.create_text_channel(
                name=self.id,
                reason=f"Ticket creation by: {interaction.user.name}",
                category=category
            )
            
            embed = discord.Embed(
                title=f"A {self.template.title} Ticket has appeared!",
                color=discord.Color.from_str("#ff6b00")
            )
            embed.set_footer(
                text="Powered by MiKontrol"
            )

            embed.add_field(
                name="Reporter",
                value=f"{interaction.user.mention}",
                inline=True
            )
            embed.add_field(
                name="Report Date",
                value=f"<t:{round(datetime.now().timestamp())}:f>",
                inline=True
            )

            for field in self.children:
                assert isinstance(field, discord.ui.Label)
                
                title=field.text
                value = ""
                if isinstance(field.component, discord.ui.TextInput):
                    value=field.component.value
                else:
                    if isinstance(field.component, (discord.ui.Select)):
                        value=field.component.values[0]
                    elif isinstance(field.component, (discord.ui.RoleSelect)):
                        value=f"<@&{field.component.values[0].id}>"
                    elif isinstance(field.component, (discord.ui.UserSelect)):
                        value=f"<@{field.component.values[0].id}>"

                embed.add_field(
                    name=title,
                    value=value,
                    inline=False
                )

            await text_channel.send(embed=embed, view=button)
            await text_channel.send( f"<@&{agent_ping.id}>" + f" <@{interaction.user.id}>" )

            self.stop()

            await ticket_create(
                guild_id=interaction.guild_id,
                ticket_type=self.template.title,
                ticket_id=self.id,
                author_id=interaction.user.id,
                ticket_channel=text_channel.id,
                ticket_category=text_channel.category_id,
                agent_role_id=agent_ping.id
            )
            
            await interaction.response.send_message(f"Your ticket has been opened https://discord.com/channels/{interaction.guild_id}/{text_channel.id}", delete_after=10, ephemeral=True)
        else:
            await interaction.response.send_message("Your ticket could not be created due to error... Try again later", delete_after=10, ephemeral=True)
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
