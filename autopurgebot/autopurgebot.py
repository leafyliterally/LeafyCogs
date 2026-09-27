import discord
from redbot.core import commands, Config


class AutoPurgeBot(commands.Cog):
    """Traps spam bots in a designated channel and auto-softbans anyone who posts there."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=847_362_951, force_registration=True)
        self.config.register_guild(channel_id=None, enabled=False, warning_message_id=None)

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group()
    async def autopurgebot(self, ctx: commands.Context):
        """Configure the spam-bot trap channel."""

    @autopurgebot.command(name="channel")
    async def autopurgebot_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the spam-bot trap channel for this server."""
        if await self.config.guild(ctx.guild).enabled():
            await ctx.send(
                "The trap is currently enabled. Disable it first with "
                f"`{ctx.clean_prefix}autopurgebot toggle false` before changing the channel."
            )
            return
        await self.config.guild(ctx.guild).channel_id.set(channel.id)
        await ctx.send(f"Spam-bot trap channel set to {channel.mention}.")

    @autopurgebot.command(name="toggle")
    async def autopurgebot_toggle(self, ctx: commands.Context, enabled: bool = None):
        """Enable or disable the spam-bot trap. Omit the argument to flip the current setting."""
        guild = ctx.guild
        if enabled is None:
            enabled = not await self.config.guild(guild).enabled()

        if enabled:
            channel_id = await self.config.guild(guild).channel_id()
            if channel_id is None:
                await ctx.send(
                    "Set a trap channel first with "
                    f"`{ctx.clean_prefix}autopurgebot channel <#channel>`."
                )
                return
            channel = guild.get_channel(channel_id)
            if channel is None:
                await ctx.send("The configured channel no longer exists. Set a new one first.")
                return

            embed = discord.Embed(
                title="DO NOT SEND MESSAGES IN THIS CHANNEL",
                description=(
                    "This channel is used to catch spam bots. Any messages sent here "
                    "will result in a softban."
                ),
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/487399523392684043.png")
            try:
                message = await channel.send(embed=embed)
            except discord.HTTPException:
                await ctx.send(
                    f"Couldn't send the warning message in {channel.mention}. "
                    "Check my permissions there."
                )
                return

            await self.config.guild(guild).warning_message_id.set(message.id)
            await self.config.guild(guild).enabled.set(True)
            await ctx.send(f"Spam-bot trap enabled in {channel.mention}.")
        else:
            await self.config.guild(guild).enabled.set(False)
            channel_id = await self.config.guild(guild).channel_id()
            message_id = await self.config.guild(guild).warning_message_id()
            if channel_id is not None and message_id is not None:
                channel = guild.get_channel(channel_id)
                if channel is not None:
                    try:
                        old_message = await channel.fetch_message(message_id)
                        await old_message.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass
            await self.config.guild(guild).warning_message_id.set(None)
            await ctx.send("Spam-bot trap disabled.")

    @autopurgebot.command(name="settings")
    async def autopurgebot_settings(self, ctx: commands.Context):
        """Show the current spam-bot trap settings for this server."""
        data = await self.config.guild(ctx.guild).all()
        channel = ctx.guild.get_channel(data["channel_id"]) if data["channel_id"] else None
        embed = discord.Embed(title="AutoPurgeBot Settings", color=discord.Color.blurple())
        embed.add_field(name="Channel", value=channel.mention if channel else "Not set", inline=False)
        embed.add_field(name="Enabled", value=str(data["enabled"]), inline=False)
        embed.add_field(
            name="Warning message bound",
            value=str(data["warning_message_id"] is not None),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return

        data = await self.config.guild(message.guild).all()
        if not data["enabled"] or data["channel_id"] != message.channel.id:
            return

        author = message.author
        is_exempt = (
            author == message.guild.owner
            or author.guild_permissions.manage_messages
            or author.guild_permissions.administrator
            or await self.bot.is_automod_immune(message)
        )
        if is_exempt:
            try:
                await message.add_reaction("❌")
            except discord.HTTPException:
                pass
            return

        await self._softban(message)

    async def _softban(self, message: discord.Message):
        guild = message.guild
        member = message.author
        reason = f"Posted in the spam-trap channel #{message.channel.name} — automatic softban."

        try:
            await member.send(
                f"You were kicked out from **{guild.name}** "
                f"for sending a message in the designated spam-trap channel. "
                f"This channel exists solely to catch spam bots. If your account is "
                f"under this condition, take action immediately for your account safety. "
                f"If this was a mistake, contact a server admin."
            )
        except discord.HTTPException:
            pass  # DMs closed — proceed anyway

        try:
            await guild.ban(member, reason=reason, delete_message_days=1)
        except discord.HTTPException:
            try:
                await message.add_reaction("❌")
            except discord.HTTPException:
                pass
            return

        try:
            await guild.unban(member, reason="Automatic softban cleanup")
        except discord.HTTPException:
            pass
