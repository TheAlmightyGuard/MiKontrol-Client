import discord
from discord import Member
from models.moderation import WarningEntry
from bot.embeds.warnings import create_warning_embed

class WarningsView(discord.ui.View):
    def __init__(self, warnings: list[WarningEntry], target : Member):
        super().__init__(timeout=120)
        self.warnings = warnings
        self.index = 0
        self.maxIndex = len(warnings) - 1
        self.currentObj = warnings[0] if warnings else None
        self.target = target
        self.update_buttons()

    def update_buttons(self):
        self.previous_page.disabled = (self.index == 0)
        self.next_page.disabled = (self.index == self.maxIndex)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index - 1 >= 0:
            self.index -= 1
            
            self.update_buttons()
            await self.fetch_page(self.index, interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index + 1 <= self.maxIndex:
            self.index += 1

            self.update_buttons()
            await self.fetch_page(self.index, interaction)
        else:
            await interaction.response.defer()

    async def fetch_page(self, page: int, interaction: discord.Interaction):

        self.currentObj = self.warnings[page]

        await interaction.response.edit_message(
            embed=create_warning_embed(self.warnings, page, interaction.user, self.target),
            view=self
        )
