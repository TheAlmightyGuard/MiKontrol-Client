import discord
import os

from discord.ext import commands
from utils.cogs_functions import CogsStatus

from models.internal import CogModel
from rich.console import Console

# To change so all modals created that has buttons have synced in
from bot.modals.ticketModal.samples.modals.moderation import ModerationModalView
from bot.modals.ticketModal.samples.modals.developer import DeveloperModalView
from bot.modals.ticketModal.template.ticketTemplate import TicketModalView

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

console = Console()
class MiBotClient(commands.Bot):
    cogStatus: CogsStatus
    
    def __init__(self):
        super().__init__(
            intents=intents,
            command_prefix="!",  # You can customize the command prefix here
        )

        self.cogStatus = CogsStatus()

    async def setup_hook(self):

        # Load event cogs
        for file in os.listdir('./bot/events'):
            if file.endswith('.py'):
                cog = f'bot.events.{file[:-3]}'

                try:
                    await self.load_extension(cog)
                except Exception as e:
                    print(f'Failed to load extension {cog}, skipping. Error: {e}')

        # Load command cogs
        for folder in os.listdir('./bot/commands'):
            for file in os.listdir(f'./bot/commands/{folder}'):
                if file.endswith('.py'):
                    cog = f'bot.commands.{folder}.{file[:-3]}'
                    try:
                        await self.load_extension(cog)
                    except Exception as e:
                        self.cogStatus.cog_status_append(
                            CogModel(
                                commandName=file.capitalize()[:-3],
                                filePath=f'./bot/commands/{folder}/{file}',
                                status=False,
                                error=str(e)
                            )
                        )
        self.cogStatus.cogs_status()

        self.add_view(view=ModerationModalView())
        self.add_view(view=DeveloperModalView())
        self.add_view(view=TicketModalView())
                
    async def close(self):
        console.log("Shutting down bot...")


def create_client() -> MiBotClient:
    return MiBotClient()

    
