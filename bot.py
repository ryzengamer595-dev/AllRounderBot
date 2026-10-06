import discord
from discord.ext import commands
from config import TOKEN, PREFIX, STATUS_TEXT

# -----------------------------
# INTENTS
# -----------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# -----------------------------
# BOT
# -----------------------------

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# -----------------------------
# BOT READY
# -----------------------------

@bot.event
async def on_ready():
    print("=" * 45)
    print(f"Bot Name : {bot.user}")
    print(f"Bot ID   : {bot.user.id}")
    print(f"Servers  : {len(bot.guilds)}")
    print("Status   : ONLINE")
    print("=" * 45)

    activity = discord.Game(name=STATUS_TEXT)
    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )


# -----------------------------
# MEMBER JOIN
# -----------------------------

@bot.event
async def on_member_join(member):
    print(f"[JOIN] {member} joined {member.guild.name}")

    # System channel mein welcome message
    channel = member.guild.system_channel

    if channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=(
                f"Welcome {member.mention} to **{member.guild.name}**!\n\n"
                "Enjoy your stay! ❤️"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)


# -----------------------------
# MEMBER LEAVE
# -----------------------------

@bot.event
async def on_member_remove(member):
    print(f"[LEAVE] {member} left {member.guild.name}")


# -----------------------------
# PING COMMAND
# -----------------------------

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)

    await ctx.send(
        f"🏓 Pong!\n"
        f"Latency: **{latency}ms**"
    )


# -----------------------------
# SERVER INFO
# -----------------------------

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.blurple()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(
        name="👑 Owner",
        value=str(guild.owner),
        inline=False
    )

    embed.add_field(
        name="👥 Members",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="💬 Channels",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="🆔 Server ID",
        value=str(guild.id),
        inline=False
    )

    await ctx.send(embed=embed)


# -----------------------------
# USER INFO
# -----------------------------

@bot.command()
async def userinfo(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title="👤 User Information",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="Username",
        value=str(member),
        inline=False
    )

    embed.add_field(
        name="ID",
        value=str(member.id),
        inline=False
    )

    embed.add_field(
        name="Joined Server",
        value=discord.utils.format_dt(
            member.joined_at,
            style="F"
        ) if member.joined_at else "Unknown",
        inline=False
    )

    await ctx.send(embed=embed)


# -----------------------------
# CLEAR COMMAND
# -----------------------------

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):

    if amount < 1:
        await ctx.send("❌ Amount must be at least 1.")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)

    message = await ctx.send(
        f"🧹 Deleted **{len(deleted) - 1}** messages."
    )

    await message.delete(delay=5)


# -----------------------------
# BAN COMMAND
# -----------------------------

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):

    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself.")
        return

    try:
        await member.ban(reason=reason)

        await ctx.send(
            f"🔨 **{member}** has been banned.\n"
            f"Reason: **{reason}**"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to ban this member."
        )


# -----------------------------
# KICK COMMAND
# -----------------------------

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):

    if member == ctx.author:
        await ctx.send("❌ You cannot kick yourself.")
        return

    try:
        await member.kick(reason=reason)

        await ctx.send(
            f"👢 **{member}** has been kicked.\n"
            f"Reason: **{reason}**"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ I don't have permission to kick this member."
        )


# -----------------------------
# ERROR HANDLER
# -----------------------------

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "❌ You don't have permission to use this command."
        )

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "❌ Missing argument. Please check the command."
        )

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(
            "❌ Member not found."
        )

    elif isinstance(error, commands.CommandNotFound):
        return

    else:
        print(f"[ERROR] {error}")


# -----------------------------
# START BOT
# -----------------------------

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable is missing!"
    )

bot.run(TOKEN)