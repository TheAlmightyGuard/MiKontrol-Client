from datetime import datetime
from discord.ext import commands
from discord import app_commands, Embed, Color, Forbidden, User
import discord
from bot.client import MiBotClient

from models.internal import CogModel

from typing import Optional
from utils.time_functions import add_time
from services.moderation_services import add_ban, remove_ban

import uuid
import inspect

from rich.console import Console

console = Console()

class Ban(commands.Cog):
    def __init__(self, client : MiBotClient):
        self.client = client
    
    async def cog_load(self):
        for command in self.get_commands():
            if isinstance(command, commands.HybridCommand):
                self.client.cogStatus.cog_status_append(
                    CogModel(
                        commandName=command.name.capitalize(),
                        filePath=inspect.getfile(command.callback),
                        status=True,
                        error=None
                    )
                )

    # +-----------------+
    # |   Ban Command   |
    # +-----------------+

    @commands.hybrid_command(
        name="ban",
        description="Ban a specified user"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        user="Specific user to ban",
        reason="Reason for ban",
        duration_or_reason="Enter reason or duration with number and a suffix of [s/m/h/d]"
    )
        
    async def ban(self, ctx : commands.Context, user : User, duration_or_reason : Optional[str] = "No reason provided.", *, reason : str = "No reason provided."):
        
        if user.bot:
            await ctx.send("Yeah, im not banning myself. Smh...", ephemeral=True)
            return
        
        actionId = str(uuid.uuid7())

        try:
            await ctx.guild.fetch_ban(user)
            await ctx.send("This user is already banned from the server.", ephemeral=True)
            return
        except discord.NotFound:
            pass
        except discord.Forbidden:
            await ctx.send("Unable to check ban status of this user due to permission and/or hierarchy.", ephemeral=True)
            return
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}", ephemeral=True)
            return
        
        # Add time from current time. Returns None if not a duration
        delta = add_time(duration_or_reason, datetime.now())
        delta_type = isinstance(delta, datetime)

        # Ban User first
        try:
            await ctx.guild.ban(
                user=user,
                reason = reason if delta_type else duration_or_reason
            )
        except discord.NotFound:
            await ctx.send("This user was not found in the server.", ephemeral=True)
            return
        except discord.Forbidden:
            await ctx.send("Unable to ban this user due to permission and/or hierarchy.", ephemeral=True)
            return
        except Exception as e:
            await ctx.send(f"An unexpected error occurred while trying to ban the user: {e}", ephemeral=True)
            return

        # Redis Task (if required)
        await add_ban(
            actionId=actionId,
            guildId=ctx.guild.id,
            type='T_BAN' if delta_type else 'BAN',
            moderatorId=ctx.author.id,
            targetId=user.id,
            expiresAt=delta,
            reason=reason if delta_type else duration_or_reason
        )        

        # Embed Creation
        embed = Embed(
            title="🔨 Moderator Action",
            description=f"{user.mention} has been banned!",
            timestamp=datetime.now(),
            color=Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Duration:",
            value=f"<t:{round(delta.timestamp())}:R>" if delta_type else "Indefinite"
        )
        embed.add_field(
            name="Reason:",
            value=reason if delta_type else duration_or_reason
        )
        embed.add_field(
            name="Issued by:",
            value=ctx.author.mention,
            inline=False
        )
        embed.set_footer(
            text=f"Action ID: {actionId}",
            icon_url=ctx.author.display_avatar.url 
        )

        await ctx.send(embed=embed)

    # +-------------------+
    # |   Unban Command   |
    # +-------------------+

    @commands.hybrid_command(
        name="unban",
        description="Unban a specified user"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        user="Specific user to unban",
        reason="Reason for unban",
    )
    async def unban(self, ctx : commands.Context, user : User, *, reason : str = "No reason provided."):
    
        if user.bot:
            await ctx.send("Yeah, im not unbanning myself. Smh...", ephemeral=True)
            return

        # Change data on ban through following flow..
        # For Temp: Delete redis task, delete task from DB then switch moderation log "active" to false
        # For permanent: Switch moderation log "active" to false
        # Both ways will return a "ModerationLog" object unless log was never found.
        result = await remove_ban(user.id, ctx.guild.id, ctx.author.id, reason)

        actionId = str(uuid.uuid7())

        # If no log was found, system will attempt to force unban either way without data returned to display as embed
        if result is None:
            await ctx.send("This person is currently not banned from our data, attemping to force unban...", ephemeral=True)

            await ctx.guild.unban(user, reason=f"Tasked by {ctx.author.name}. Reason: {reason}")
            await ctx.send(f"{user.mention} has been unbanned!")
            return


        await ctx.guild.unban(user, reason=f"Tasked by {ctx.author.name}. Reason: {reason}")

        embed = Embed(
            title="🔨 Moderator Action",
            description=f"{user.mention} has been unbanned!",
            timestamp=datetime.now(),
            color=Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Time remaining:",
            value=f"<t:{round(result.expiresAt.timestamp())}:R>" if isinstance(result.expiresAt, datetime) else "Indefinite",
            inline=True
        )
        embed.add_field(
            name="Reason Given:",
            value=result.reason,
            inline=True
        )
        embed.add_field(
            name="Reason for Removal:",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="Actioned by:",
            value=ctx.author.mention
        )
        embed.set_footer(
            text=f"Action ID: {actionId}",
            icon_url=ctx.author.display_avatar.url 
        )

        await ctx.send(embed=embed)

    
    # +------------------+
    # |  Error Handler   |
    # +------------------+

    @ban.error
    @unban.error
    async def ban_error(self, ctx : commands.Context, error : commands.CommandError):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Error! Bad Argument, please input proper arguments!", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Error! You lack permission to execute this command!", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Error! Bot is missing permissions to execute this command!", ephemeral=True)
        elif isinstance(error, discord.NotFound):
            await ctx.send("Error! The specified user was not found!", ephemeral=True)
        elif isinstance(error, Forbidden):
            await ctx.send("Error! Bot lacks the necessary permissions to execute this command!", ephemeral=True)
            console.log(f"Unexpected error! Type: {type(error)} \n Error: {error}")
    



async def setup(client : MiBotClient):
    await client.add_cog(Ban(client))