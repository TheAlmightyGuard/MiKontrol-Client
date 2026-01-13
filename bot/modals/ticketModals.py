import discord, uuid, os
from datetime import datetime

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

        assert isinstance(self.topic.component, discord.ui.Select)
        assert isinstance(self.violation.component, discord.ui.Select)
        assert isinstance(self.evidence.component, discord.ui.TextInput)

        ticket_id = str(uuid.uuid7())

        category = discord.utils.get(interaction.guild.categories, id=os.getenv("MUTED_CATEGORY"))
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
            name="Report Date:",
            value=f"<t:{round(datetime.now().timestamp())}:f>",
            inline=True
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

        await text_channel.send(embed=embed)
        await text_channel.send(f"@everyone") # To replace with pinging mod role and reporter user
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)
