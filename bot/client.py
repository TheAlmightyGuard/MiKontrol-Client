import discord
import os

from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MiBotClient(commands.Bot):
    
    def __init__(self):
        super().__init__(
            intents=intents,
            command_prefix="!",  # You can customize the command prefix here
        )

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
                        print(f'Failed to load extension {cog}, skipping. Error: {e}')
                

def create_client() -> MiBotClient:
    return MiBotClient()
    
