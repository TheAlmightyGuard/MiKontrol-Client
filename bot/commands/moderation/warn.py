from datetime import datetime
from discord.ext import commands
from discord import app_commands, Member, Embed, Color, Forbidden, NotFound
from bot.client import MiBotClient
from models.internal import CogModel
from models.moderation import WarningEntry

from services.moderation_services import add_warning, remove_warning, list_warnings
from bot.embeds.warnings import create_warning_embed, create_empty_embed
from bot.views.paginator_view import WarningsView

import uuid
import inspect

from rich.console import Console

console = Console()

class Warn(commands.Cog):
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
    # +----------------------+
    # |  Warn Group Command  |
    # +----------------------+

    @commands.hybrid_command(
        name="warn",
        description="Issue a warning for a specified user"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        user="The user to add warning to",
        reason="Reason for warning",
    )
    async def warn(self, ctx : commands.Context, user : Member, *, reason : str = "No reason provided."):
        
        if user.bot:
            await ctx.send("Yeah, im not warning myself. Smh...", ephemeral=True)
            return
        
        actionId = str(uuid.uuid7())
        # Post warn entry
        await add_warning(
            actionId=actionId,
            guildId=ctx.guild.id,
            targetId=user.id,
            moderatorId=ctx.author.id,
            reason=reason
        )
        
        embed = Embed(
            title="⚠️ Issued a Warning",
            description=f"A warning has been issued to {user.mention}",
            color=Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Reason for Warning:", value=reason, inline=True)
        embed.add_field(name="Issued by:", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Action ID: {actionId}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


    # +-----------------------+
    # |  Remove Warn Command
    # +-----------------------+

    @commands.hybrid_command(
        name="delwarn",
        aliases=["rwarn"],
        description="Remove a warning from a user"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        warning_id="Action ID of the warning to remove",
        reason="Reason for removing the warning",
    )
    async def remove_warn(self, ctx : commands.Context, warning_id : str, *, reason : str = "No reason provided."):
        
        result : WarningEntry | None = await remove_warning(
            actionId=warning_id,
            guildId=ctx.guild.id,
            moderatorId=ctx.author.id,
            reason=reason
        )

        if result is None:
            await ctx.send("Warning not found. Cannot complete removal.")
            return

        actionId = str(uuid.uuid7())

        user = ctx.guild.get_member(result.targetId)

        if user is None:
            try:
                user = await ctx.guild.fetch_member(result.targetId)
            except Forbidden:
                raise commands.BotMissingPermissions()
            except NotFound:
                raise NotFound()
            except Exception:
                await ctx.send("An unexpected error occurred while fetching the user.")
                return

        embed = Embed(
            title="⚠️ Lifted a Warning",
            description=f"A warning has been lifted from {user.mention}",
            color=Color.orange(),
            timestamp=datetime.now()
        )

        embed.add_field(name="Reason Given:", value=result.reason, inline=True)
        embed.add_field(name="Date of Issue:", value=f"<t:{round(datetime.now().timestamp())}:f>", inline=True)
        embed.add_field(name="Reason for Removal:", value=reason, inline=False)
        embed.add_field(name="Actioned by:", value=ctx.author.mention, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Action ID: {actionId}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)



    # +-----------------------+
    # |  List Warn Command
    # +-----------------------+

    @commands.hybrid_command(
        name="warns",
        aliases=["listwarns", "listwarnings"],
        description="List all warnings from user"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        user="Specified user to list warnings from",
    )
    async def list_warns(self, ctx : commands.Context, user : Member):
        result = await list_warnings(
            serverId=ctx.guild.id,
            userId=user.id
        )

        if result is None:
            
            await ctx.send(
                embed=create_empty_embed(ctx.author, user)
            )

        else:
            await ctx.send(
                embed=create_warning_embed(result, 0, ctx.author, user),
                view=WarningsView(result, user)
            )


    # +------------------+
    # |  Error Handler
    # +------------------+

    @warn.error
    @remove_warn.error
    async def mute_error(self, ctx : commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Bad Argument Error!", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You lack permission to execute this command!", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot is missing permissions to execute this command!", ephemeral=True)
        elif isinstance(error, Forbidden):
            await ctx.send("Cannot execute command on higher permission user!", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown! Try again in {round(error.retry_after, 2)} seconds.", ephemeral=True)
        elif isinstance(error, commands.HybridCommandError):
            await ctx.send(f"Hybrid Command Error! Type: {error.original}", ephemeral=True)
        else:
            await ctx.send(f"Unexpected error! Type: {type(error)} \n Error: {error}", ephemeral=True)
            console.log(f"Unexpected error! Type: {type(error)} \n Error: {error}")




async def setup(client : MiBotClient):
    await client.add_cog(Warn(client))