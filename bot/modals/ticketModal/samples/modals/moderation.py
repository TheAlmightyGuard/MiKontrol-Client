import discord, os, asyncio
from datetime import datetime

from services.ticket_services import ticket_create, ticket_assign, ticket_close, ticket_pull
from utils.get_fetch import get_channel, get_role
from utils.time_functions import add_time
class ModerationModalView(discord.ui.View):
    def __init__(self, modal = None, agent : discord.Role = None):
        self.modal = modal
        self.role = agent
        self.error = None
        super().__init__(timeout=None)

    @discord.ui.button(label="💼 Take the case", style=discord.ButtonStyle.grey, custom_id="req:case_accept")
    async def case_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        agentId = self.role.id
        if not (interaction.user.get_role(agentId) or interaction.user.guild_permissions.kick_members):
            await interaction.response.send_message(
                content=f"{interaction.user.mention} You don't have permissions to accept tickets!",
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
                content=f"{interaction.user.mention} You cannot accept to moderate a ticket against you / you created yourself!",
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
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel

        if channel is None:
            return
        
        agent = await ticket_pull(channel.name)
        authorized = False

        if agent == 0:
            if interaction.user.guild_permissions.administrator:
                authorized = True
            else:
                await interaction.response.send_message(f"{interaction.user.mention} You do not have permission to close unclaimed tickets!", ephemeral=True, delete_after=5)
                return
        else:
            if agent == interaction.user.id:
                authorized = True
            else:
                await interaction.response.send_message(f"{interaction.user.mention} Unauthorized action. You are not the agent of this ticket.", delete_after=5, ephemeral=True)
                return


        if authorized:
            await ticket_close(channel.name, interaction.user.id, f"Agent {interaction.user.name} ({interaction.user.id}) has closed the ticket.")
            await interaction.response.send_message(f"Agent {interaction.user.mention} ({interaction.user.id}) has closed this ticket. Closing <t:{round(add_time("5s", datetime.now()).timestamp())}:R>", delete_after=5, ephemeral=True)
            await asyncio.sleep(5)
            await interaction.channel.delete(reason=f"Agent {interaction.user.name} ({interaction.user.id}) has closed the ticket.")

class ModerationModal(discord.ui.Modal, title="Open a ticket [ Moderation ]"):

    
    violator = discord.ui.Label(
        text='Offender',
        description='Enter the name of the Violator',
        component=discord.ui.UserSelect(
            placeholder="Choose a member",
            required=True
        ),
    )

    environment = discord.ui.Label(
        text='Report Environment',
        description='Select the type of the environment.',
        component=discord.ui.Select(
            placeholder='Choose an environment type...',
            options=[
                discord.SelectOption(label='Text Message', description='Violation was conducted in a text message environment'),
                discord.SelectOption(label='Voice Message', description='Violation was conducted in a voice transmitted environment')
            ],
        ),
    )

    violation = discord.ui.Label(
        text='Type of Violation',
        description='Select the type of violation',
        component=discord.ui.Select(
            placeholder='Choose a violation...',
            options=[
                discord.SelectOption(label='Harassment', description='Harassed other members'),
                discord.SelectOption(label='Spam', description='Spammed within environment'),
                discord.SelectOption(label='NSFW', description='Posted NSFW content within environment'),
                discord.SelectOption(label='Hate Speech', description='Conducting hate speech directly / indirectly others'),
                discord.SelectOption(label='Others', description='Anything that are not above to be reported'),
            ],
        ),
    )

    evidence = discord.ui.Label(
        text='Evidence',
        description='Enter your evidence',
        component=discord.ui.TextInput(
            placeholder="Enter evidence(s) link here"
        )
    )

    async def on_submit(self, interaction: discord.Interaction):

        category = await get_channel(interaction.guild, os.getenv("TICKET_CATEGORY"))
        agent_ping = await get_role(interaction.guild, os.getenv("MOD_ROLE"))

        assert isinstance(self.environment.component, discord.ui.Select)
        assert isinstance(self.violation.component, discord.ui.Select)
        assert isinstance(self.evidence.component, discord.ui.TextInput)
        assert isinstance(self.violator.component, discord.ui.UserSelect)

        if agent_ping is not None:

            buttons = ModerationModalView(self, agent_ping)

            text_channel = await interaction.guild.create_text_channel(
                name=self.id,
                reason=f"Ticket creation by: {interaction.user.name}",
                category=category
            )
            
            embed = discord.Embed(
                title="A Moderator Ticket has appeared!",
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
                name="Offender",
                value=f"{self.violator.component.values[0].mention}",
                inline=True
            )
            embed.add_field(
                name="Report Date",
                value=f"<t:{round(datetime.now().timestamp())}:f>",
                inline=False
            )
            embed.add_field(
                name="Report Environment",
                value=f"{self.environment.component.values[0]}",
                inline=False
            )
            embed.add_field(
                name="Report Type",
                value=f"{self.violation.component.values[0]}",
                inline=False
            )
            embed.add_field(
                name="Evidence",
                value=f"{self.evidence.component.value}",
                inline=False
            )

            await text_channel.send(embed=embed, view=buttons)
            self.msg = await text_channel.send( f"<@&{agent_ping.id}>" + f" <@{interaction.user.id}>" )

            self.stop()

            await ticket_create(
                guild_id=interaction.guild_id,
                ticket_type="Moderation",
                ticket_id=self.id,
                author_id=interaction.user.id,
                ticket_channel=text_channel.id,
                ticket_category=text_channel.category_id,
                agent_role_id=agent_ping.id
            )
            
            
            await interaction.response.send_message(f"Your ticket has been opened https://discord.com/channels/{interaction.guild_id}/{text_channel.id}", delete_after=10, ephemeral=True)

        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
