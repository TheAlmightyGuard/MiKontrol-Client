import discord, uuid, os
from datetime import datetime

class ModerationModalView(discord.ui.View):
    def __init__(self, modal : ModerationModal = None):
        self.modal = modal
        self.error = None
        super().__init__(timeout=None)

    @discord.ui.button(label="[MOD] Take the case", style=discord.ButtonStyle.primary, custom_id="persistent:mod_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = interaction.message.embeds[0]
        embed = embed.copy()

        violatorId = ""
        for field in embed.fields:
            if field.name == "Offender":
                violatorId = int(field.value[2:-1])


        if interaction.user.id == violatorId:

            self.error = await interaction.response.send_message(
                content="You cannot accept to moderate a ticket against you!",
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

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )



class ModerationModal(discord.ui.Modal, title="Open a ticket [ ??? ]"):
    violator = discord.ui.Label(
        text='Offender',
        description='Enter the name of the Violator',
        component=discord.ui.UserSelect(
            placeholder="Choose a member",
            required=True
        ),
    )

    topic = discord.ui.Label(
        text='Report Type',
        description='Select the type of the report.',
        component=discord.ui.Select(
            placeholder='Choose a type...',
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

        buttons = ModerationModalView(self)

        assert isinstance(self.topic.component, discord.ui.Select)
        assert isinstance(self.violation.component, discord.ui.Select)
        assert isinstance(self.evidence.component, discord.ui.TextInput)
        assert isinstance(self.violator.component, discord.ui.UserSelect)

        ticket_id = str(uuid.uuid7())

        category = interaction.guild.get_channel(os.getenv("TICKET_CATEGORY"))

        if category is None:
            try:
                category = await interaction.guild.fetch_channel(os.getenv("TICKET_CATEGORY"))
            except Exception as e:
                category = None

        mod_role = interaction.guild.get_role(os.getenv("MOD_ROLE"))
        
        if mod_role is None:
            try:
                mod_role = await interaction.guild.fetch_role(os.getenv("MOD_ROLE"))
            except Exception as e:
                mod_role = None

        mod_mention = ""

        if mod_role is not None:
            mod_mention = f"<@&{mod_role.id}>"



        text_channel = await interaction.guild.create_text_channel(
            name=ticket_id,
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
            name="Report Date:",
            value=f"<t:{round(datetime.now().timestamp())}:f>",
            inline=False
        )
        embed.add_field(
            name="Report Environment",
            value=f"{self.topic.component.values[0]}",
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
        self.msg = await text_channel.send( mod_mention + f"<@{interaction.user.id}>" ) # To replace with pinging mod role and reporter user

        await interaction.response.send_message(f"Your ticket has been opened https://discord.com/channels/{interaction.guild_id}/{text_channel.id}")
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
