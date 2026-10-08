import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


# ============================================================
# TICKET CONFIGURATION
# ============================================================

TICKET_CATEGORY = "Tickets"
STAFF_ROLE = "Support Team"

# ============================================================
# TICKET PANEL DESIGN
# ============================================================

PANEL_TITLE = "🎫 Support Tickets"

PANEL_DESCRIPTION = (
    "Need help? We are here for you!\n\n"
    "Please select the option below that matches your issue.\n"
    "Our staff will assist you as soon as possible."
)

PANEL_COLOR = 0x5865F2

# Put direct image URLs here if you want a banner/thumbnail.
# Leave empty if you don't want them.
PANEL_BANNER = ""
PANEL_THUMBNAIL = ""

PANEL_FOOTER = "AllRounderBot • Ticket System"


# ============================================================
# TICKET OPTIONS
# ============================================================

TICKET_OPTIONS = [
    {
        "label": "Support",
        "emoji": "🛠️",
        "description": "Need help with the server or bot?",
        "prefix": "support",
    },
    {
        "label": "Report",
        "emoji": "🚨",
        "description": "Report a member or server issue.",
        "prefix": "report",
    },
    {
        "label": "Purchase",
        "emoji": "💳",
        "description": "Questions about purchases or payments.",
        "prefix": "purchase",
    },
    {
        "label": "Other",
        "emoji": "❓",
        "description": "Something else? We can help.",
        "prefix": "other",
    },
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_staff_role(guild: discord.Guild):
    return discord.utils.get(
        guild.roles,
        name=STAFF_ROLE
    )


def get_ticket_category(guild: discord.Guild):
    return discord.utils.get(
        guild.categories,
        name=TICKET_CATEGORY
    )


def is_ticket_channel(channel):
    return (
        isinstance(channel, discord.TextChannel)
        and channel.topic is not None
        and channel.topic.startswith("allrounder-ticket:")
    )


# ============================================================
# TICKET PANEL VIEW
# ============================================================

class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        for option in TICKET_OPTIONS:
            self.add_item(TicketButton(option))


class TicketButton(discord.ui.Button):

    def __init__(self, option):
        super().__init__(
            label=option["label"],
            emoji=option["emoji"],
            style=discord.ButtonStyle.green,
            custom_id="allrounder:ticket:" + option["prefix"]
        )

        self.option = option

    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild

        if guild is None:
            return

        # Check if user already has a ticket
        existing = discord.utils.find(
            lambda channel:
                isinstance(channel, discord.TextChannel)
                and channel.topic is not None
                and channel.topic.startswith(
                    "allrounder-ticket:" + str(interaction.user.id) + ":"
                ),
            guild.text_channels
        )

        if existing:
            await interaction.response.send_message(
                "❌ You already have a ticket: " + existing.mention,
                ephemeral=True
            )
            return

        # Find or create ticket category
        category = get_ticket_category(guild)

        if category is None:
            try:
                category = await guild.create_category(
                    TICKET_CATEGORY,
                    reason="Creating ticket category"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to create categories.",
                    ephemeral=True
                )
                return

        # Get staff role
        staff_role = get_staff_role(guild)

        # Channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            ),

            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
                attach_files=True,
                embed_links=True
            )

        # Create ticket channel
        ticket_name = (
            self.option["prefix"] + "-" + interaction.user.name
        ).lower()

        try:
            channel = await guild.create_text_channel(
                ticket_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    "allrounder-ticket:"
                    + str(interaction.user.id)
                    + ":"
                    + self.option["prefix"]
                ),
                reason=(
                    self.option["label"]
                    + " ticket created by "
                    + str(interaction.user)
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create the ticket.",
                ephemeral=True
            )
            return

        # Ticket embed
        embed = discord.Embed(
            title=(
                self.option["emoji"]
                + " "
                + self.option["label"]
                + " Ticket"
            ),
            description=(
                "Welcome "
                + interaction.user.mention
                + "! 👋\n\n"
                + "**Category:** "
                + self.option["emoji"]
                + " "
                + self.option["label"]
                + "\n\n"
                + "**About this ticket:**\n"
                + self.option["description"]
                + "\n\n"
                + "Please explain your issue clearly.\n"
                + "A staff member will assist you shortly."
            ),
            color=PANEL_COLOR,
            timestamp=datetime.utcnow()
        )

        embed.set_footer(text=PANEL_FOOTER)

        mention_text = interaction.user.mention

        if staff_role:
            mention_text += " " + staff_role.mention

        await channel.send(
            content=mention_text,
            embed=embed,
            view=TicketControlView()
        )

        await interaction.response.send_message(
            "✅ Your ticket has been created: " + channel.mention,
            ephemeral=True
        )


# ============================================================
# TICKET CONTROL VIEW
# ============================================================

class TicketControlView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim",
        emoji="🙋",
        style=discord.ButtonStyle.success,
        custom_id="allrounder:claim"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff members can claim tickets.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🙋 Ticket Claimed",
            description=(
                "This ticket is now being handled by "
                + interaction.user.mention
                + "."
            ),
            color=0x57F287
        )

        await interaction.response.send_message(embed=embed)

    @discord.ui.button(
        label="Close",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="allrounder:close"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can close tickets.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 Ticket closed. Use the button below to delete it.",
            view=DeleteTicketView()
        )

    @discord.ui.button(
        label="Add User",
        emoji="➕",
        style=discord.ButtonStyle.secondary,
        custom_id="allrounder:add_user"
    )
    async def add_user(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can add users.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Use /ticketadd @user to add a member.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Remove User",
        emoji="➖",
        style=discord.ButtonStyle.secondary,
        custom_id="allrounder:remove_user"
    )
    async def remove_user(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can remove users.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Use /ticketremove @user to remove a member.",
            ephemeral=True
        )


# ============================================================
# DELETE TICKET VIEW
# ============================================================

class DeleteTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Delete Ticket",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="allrounder:delete_ticket"
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can delete tickets.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🗑️ Deleting ticket..."
        )

        await interaction.channel.delete(
            reason="Ticket deleted by " + str(interaction.user)
        )


# ============================================================
# TICKET COG
# ============================================================

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        bot.add_view(TicketView())
        bot.add_view(TicketControlView())
        bot.add_view(DeleteTicketView())

    @app_commands.command(
        name="ticket",
        description="Create the ticket panel."
    )
    @app_commands.checks.has_permissions(
        manage_channels=True
    )
    async def ticket(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title=PANEL_TITLE,
            description=PANEL_DESCRIPTION,
            color=PANEL_COLOR
        )

        if PANEL_BANNER:
            embed.set_image(url=PANEL_BANNER)

        if PANEL_THUMBNAIL:
            embed.set_thumbnail(url=PANEL_THUMBNAIL)

        embed.set_footer(
            text="Select an option below to create a ticket."
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            "✅ Ticket panel sent.",
            ephemeral=True
        )

    @app_commands.command(
        name="ticketadd",
        description="Add a member to the current ticket."
    )
    @app_commands.describe(
        member="Member to add to the ticket."
    )
    async def ticketadd(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not is_ticket_channel(interaction.channel):
            await interaction.response.send_message(
                "❌ This command can only be used inside a ticket.",
                ephemeral=True
            )
            return

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can add members.",
                ephemeral=True
            )
            return

        await interaction.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
        )

        await interaction.response.send_message(
            "✅ "
            + member.mention
            + " has been added to this ticket."
        )

    @app_commands.command(
        name="ticketremove",
        description="Remove a member from the current ticket."
    )
    @app_commands.describe(
        member="Member to remove from the ticket."
    )
    async def ticketremove(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not is_ticket_channel(interaction.channel):
            await interaction.response.send_message(
                "❌ This command can only be used inside a ticket.",
                ephemeral=True
            )
            return

        staff_role = get_staff_role(interaction.guild)

        if (
            staff_role
            and staff_role not in interaction.user.roles
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                "❌ Only staff can remove members.",
                ephemeral=True
            )
            return

        await interaction.channel.set_permissions(
            member,
            overwrite=None
        )

        await interaction.response.send_message(
            "✅ "
            + member.mention
            + " has been removed from this ticket."
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))