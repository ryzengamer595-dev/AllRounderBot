import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime


CONFIG_FILE = "ticket_config.json"


# ============================================================
# CONFIG HELPERS
# ============================================================

DEFAULT_CONFIG = {
    "title": "🎫 Support Tickets",
    "description": "Select an option below to create a ticket.",
    "staff_role_id": 0,
    "category_name": "Tickets",
    "banner": "",
    "options": []
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        config = DEFAULT_CONFIG.copy()
        config.update(data)
        return config

    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


# ============================================================
# SETUP SESSION
# ============================================================

setup_sessions = {}


# ============================================================
# TICKET HELPERS
# ============================================================

def get_staff_role(guild, config):
    role_id = config.get("staff_role_id", 0)

    if not role_id:
        return None

    return guild.get_role(role_id)


def get_ticket_category(guild, config):
    category_name = config.get("category_name", "Tickets")

    return discord.utils.get(
        guild.categories,
        name=category_name
    )


def is_ticket_channel(channel):
    return (
        isinstance(channel, discord.TextChannel)
        and channel.topic is not None
        and channel.topic.startswith("allrounder-ticket:")
    )


# ============================================================
# TICKET VIEW
# ============================================================

class TicketView(discord.ui.View):

    def __init__(self, config):
        super().__init__(timeout=None)

        options = config.get("options", [])

        for index, option in enumerate(options):
            self.add_item(
                TicketButton(option, index)
            )


class TicketButton(discord.ui.Button):

    def __init__(self, option, index):
        super().__init__(
            label=option["name"][:80],
            emoji=option.get("emoji", "🎫"),
            style=discord.ButtonStyle.primary,
            custom_id="allrounder:ticket:" + str(index)
        )

        self.option = option

    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild

        if guild is None:
            return

        config = load_config()

        # Check existing ticket
        existing = discord.utils.find(
            lambda channel:
                isinstance(channel, discord.TextChannel)
                and channel.topic is not None
                and channel.topic.startswith(
                    "allrounder-ticket:"
                    + str(interaction.user.id)
                    + ":"
                ),
            guild.text_channels
        )

        if existing:
            await interaction.response.send_message(
                "❌ You already have a ticket: "
                + existing.mention,
                ephemeral=True
            )
            return

        # Get or create category
        category = get_ticket_category(guild, config)

        if category is None:
            try:
                category = await guild.create_category(
                    config.get("category_name", "Tickets"),
                    reason="Ticket system category"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to create the ticket category.",
                    ephemeral=True
                )
                return

        # Staff role
        staff_role = get_staff_role(guild, config)

        # Permissions
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
                manage_messages=True,
                read_message_history=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        # Ticket channel name
        prefix = self.option.get("prefix", "ticket")

        ticket_name = (
            prefix
            + "-"
            + interaction.user.name
        ).lower()

        # Remove invalid characters
        ticket_name = "".join(
            character
            for character in ticket_name
            if character.isalnum() or character in "-_"
        )

        ticket_name = ticket_name[:90]

        try:
            channel = await guild.create_text_channel(
                ticket_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    "allrounder-ticket:"
                    + str(interaction.user.id)
                    + ":"
                    + prefix
                ),
                reason="Ticket created by " + str(interaction.user)
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create ticket channels.",
                ephemeral=True
            )
            return

        # Ticket embed
        embed = discord.Embed(
            title=(
                self.option.get("emoji", "🎫")
                + " "
                + self.option.get("name", "Ticket")
            ),
            description=(
                "Welcome "
                + interaction.user.mention
                + "! 👋\n\n"
                + self.option.get(
                    "description",
                    "Please explain your issue."
                )
                + "\n\n"
                + "A staff member will assist you shortly."
            ),
            color=0x5865F2,
            timestamp=datetime.utcnow()
        )

        embed.set_footer(
            text="AllRounderBot • Ticket System"
        )

        content = interaction.user.mention

        if staff_role:
            content += " " + staff_role.mention

        await channel.send(
            content=content,
            embed=embed,
            view=TicketControlView()
        )

        await interaction.response.send_message(
            "✅ Ticket created: " + channel.mention,
            ephemeral=True
        )


# ============================================================
# TICKET CONTROL
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

        config = load_config()
        staff_role = get_staff_role(
            interaction.guild,
            config
        )

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

        await interaction.response.send_message(
            embed=embed
        )

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

        config = load_config()
        staff_role = get_staff_role(
            interaction.guild,
            config
        )

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
            "🔒 Ticket closed. Use the delete button below.",
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

        await interaction.response.send_message(
            "Use /ticketremove @user to remove a member.",
            ephemeral=True
        )


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

        config = load_config()

        staff_role = get_staff_role(
            interaction.guild,
            config
        )

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
# SETUP MODALS
# ============================================================

class BasicSetupModal(discord.ui.Modal):

    def __init__(self, user_id):
        super().__init__(
            title="Ticket Setup • Basic Settings"
        )

        self.user_id = user_id

        self.title_input = discord.ui.TextInput(
            label="Panel Title",
            placeholder="Example: 🎫 Support Center",
            max_length=100,
            required=True
        )

        self.description_input = discord.ui.TextInput(
            label="Panel Description",
            placeholder="Write the description shown above the buttons.",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )

        self.category_input = discord.ui.TextInput(
            label="Ticket Category Name",
            placeholder="Example: Tickets",
            max_length=100,
            required=True,
            default="Tickets"
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.category_input)

    async def on_submit(self, interaction):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired. Run /ticket setup again.",
                ephemeral=True
            )
            return

        session["title"] = str(self.title_input.value)
        session["description"] = str(self.description_input.value)
        session["category_name"] = str(self.category_input.value)

        await interaction.response.send_message(
            "✅ Basic settings saved.\n\n"
            "Next step: select your staff role.",
            view=StaffRoleView(self.user_id),
            ephemeral=True
        )


class BannerModal(discord.ui.Modal):

    def __init__(self, user_id):
        super().__init__(
            title="Ticket Setup • Banner"
        )

        self.user_id = user_id

        self.banner_input = discord.ui.TextInput(
            label="Banner Image URL",
            placeholder="https://example.com/banner.png",
            max_length=1000,
            required=True
        )

        self.add_item(self.banner_input)

    async def on_submit(self, interaction):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired. Run /ticket setup again.",
                ephemeral=True
            )
            return

        session["banner"] = str(self.banner_input.value)

        await interaction.response.send_message(
            "✅ Banner saved.",
            view=OptionCountView(self.user_id),
            ephemeral=True
        )


class OptionModal(discord.ui.Modal):

    def __init__(self, user_id, option_number, total):
        super().__init__(
            title="Ticket Option "
            + str(option_number)
            + " / "
            + str(total)
        )

        self.user_id = user_id
        self.option_number = option_number
        self.total = total

        self.name_input = discord.ui.TextInput(
            label="Option Name",
            placeholder="Example: General Support",
            max_length=80,
            required=True
        )

        self.emoji_input = discord.ui.TextInput(
            label="Emoji",
            placeholder="Example: 🛠️",
            max_length=10,
            required=True,
            default="🎫"
        )

        self.description_input = discord.ui.TextInput(
            label="Option Description",
            placeholder="Explain what this ticket option is for.",
            style=discord.TextStyle.paragraph,
            max_length=300,
            required=True
        )

        self.add_item(self.name_input)
        self.add_item(self.emoji_input)
        self.add_item(self.description_input)

    async def on_submit(self, interaction):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired.",
                ephemeral=True
            )
            return

        options = session.setdefault("options", [])

        prefix = str(self.name_input.value).lower()
        prefix = "".join(
            character
            for character in prefix
            if character.isalnum()
        )

        if not prefix:
            prefix = "ticket"

        options.append(
            {
                "name": str(self.name_input.value),
                "emoji": str(self.emoji_input.value),
                "description": str(self.description_input.value),
                "prefix": prefix[:20]
            }
        )

        if len(options) < self.total:

            next_number = len(options) + 1

            await interaction.response.send_message(
                "✅ Option "
                + str(len(options))
                + " saved.\n\n"
                "Now setup option "
                + str(next_number)
                + ".",
                view=NextOptionView(
                    self.user_id,
                    next_number,
                    self.total
                ),
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "🎉 All ticket options have been configured!",
                view=SetupPreviewView(self.user_id),
                ephemeral=True
            )


# ============================================================
# SETUP VIEWS
# ============================================================

class StaffRoleView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=300)

        self.user_id = user_id

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Select your staff role",
        min_values=1,
        max_values=1
    )
    async def role_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.RoleSelect
    ):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired.",
                ephemeral=True
            )
            return

        role = select.values[0]

        session["staff_role_id"] = role.id

        await interaction.response.send_message(
            "✅ Staff role selected: "
            + role.mention
            + "\n\n"
            "Do you want to add a banner?",
            view=BannerChoiceView(self.user_id),
            ephemeral=True
        )


class BannerChoiceView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=300)

        self.user_id = user_id

    @discord.ui.button(
        label="Yes, Add Banner",
        emoji="🖼️",
        style=discord.ButtonStyle.success
    )
    async def yes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            BannerModal(self.user_id)
        )

    @discord.ui.button(
        label="No Banner",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def no(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired.",
                ephemeral=True
            )
            return

        session["banner"] = ""

        await interaction.response.send_message(
            "Okay, no banner will be used.",
            view=OptionCountView(self.user_id),
            ephemeral=True
        )


class OptionCountView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=300)

        self.user_id = user_id

    @discord.ui.select(
        placeholder="How many ticket options?",
        options=[
            discord.SelectOption(
                label="1 Option",
                value="1",
                emoji="1️⃣"
            ),
            discord.SelectOption(
                label="2 Options",
                value="2",
                emoji="2️⃣"
            ),
            discord.SelectOption(
                label="3 Options",
                value="3",
                emoji="3️⃣"
            ),
            discord.SelectOption(
                label="4 Options",
                value="4",
                emoji="4️⃣"
            ),
            discord.SelectOption(
                label="5 Options",
                value="5",
                emoji="5️⃣"
            ),
        ],
        min_values=1,
        max_values=1
    )
    async def count_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        count = int(select.values[0])

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired.",
                ephemeral=True
            )
            return

        session["options"] = []
        session["option_count"] = count

        await interaction.response.send_message(
            "You selected "
            + str(count)
            + " ticket options.\n\n"
            "Now let's create option 1.",
            view=NextOptionView(
                self.user_id,
                1,
                count
            ),
            ephemeral=True
        )


class NextOptionView(discord.ui.View):

    def __init__(self, user_id, option_number, total):
        super().__init__(timeout=300)

        self.user_id = user_id
        self.option_number = option_number
        self.total = total

    @discord.ui.button(
        label="Setup This Option",
        emoji="⚙️",
        style=discord.ButtonStyle.primary
    )
    async def setup_option(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            OptionModal(
                self.user_id,
                self.option_number,
                self.total
            )
        )


# ============================================================
# PREVIEW
# ============================================================

class SetupPreviewView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=300)

        self.user_id = user_id

    @discord.ui.button(
        label="Preview",
        emoji="👀",
        style=discord.ButtonStyle.secondary
    )
    async def preview(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired.",
                ephemeral=True
            )
            return

        embed = create_panel_embed(session)

        await interaction.response.send_message(
            content="Here is your ticket panel preview:",
            embed=embed,
            view=TicketView(session),
            ephemeral=True
        )

    @discord.ui.button(
        label="Confirm & Send",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        session = setup_sessions.get(self.user_id)

        if session is None:
            await interaction.response.send_message(
                "❌ Setup session expired. Run /ticket setup again.",
                ephemeral=True
            )
            return

        config = load_config()

        config.update(session)

        save_config(config)

        try:
            await interaction.channel.send(
                embed=create_panel_embed(config),
                view=TicketView(config)
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I cannot send the ticket panel in this channel.",
                ephemeral=True
            )
            return

        setup_sessions.pop(self.user_id, None)

        await interaction.response.send_message(
            "🎉 Ticket system setup complete!\n"
            "The ticket panel has been sent in this channel.",
            ephemeral=True
        )


# ============================================================
# PANEL EMBED
# ============================================================

def create_panel_embed(config):

    embed = discord.Embed(
        title=config.get(
            "title",
            "🎫 Support Tickets"
        ),
        description=config.get(
            "description",
            "Select an option below."
        ),
        color=0x5865F2
    )

    banner = config.get("banner", "")

    if banner:
        embed.set_image(url=banner)

    embed.set_footer(
        text="AllRounderBot • Ticket System"
    )

    return embed


# ============================================================
# TICKET COG
# ============================================================

class Tickets(commands.Cog):

    ticket_group = app_commands.Group(
        name="ticket",
        description="Ticket system commands."
    )

    def __init__(self, bot):

        self.bot = bot

        config = load_config()

        bot.add_view(
            TicketView(config)
        )

        bot.add_view(
            TicketControlView()
        )

        bot.add_view(
            DeleteTicketView()
        )

    @ticket_group.command(
        name="setup",
        description="Setup the ticket system."
    )
    @app_commands.checks.has_permissions(
        manage_channels=True
    )
    async def setup_ticket(
        self,
        interaction: discord.Interaction
    ):

        setup_sessions[interaction.user.id] = {
            "title": "",
            "description": "",
            "staff_role_id": 0,
            "category_name": "Tickets",
            "banner": "",
            "options": []
        }

        await interaction.response.send_modal(
            BasicSetupModal(
                interaction.user.id
            )
        )

    @app_commands.command(
        name="ticketadd",
        description="Add a member to the current ticket."
    )
    @app_commands.describe(
        member="Member to add."
    )
    async def ticketadd(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not is_ticket_channel(
            interaction.channel
        ):
            await interaction.response.send_message(
                "❌ This command can only be used inside a ticket.",
                ephemeral=True
            )
            return

        config = load_config()

        staff_role = get_staff_role(
            interaction.guild,
            config
        )

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
        member="Member to remove."
    )
    async def ticketremove(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if not is_ticket_channel(
            interaction.channel
        ):
            await interaction.response.send_message(
                "❌ This command can only be used inside a ticket.",
                ephemeral=True
            )
            return

        config = load_config()

        staff_role = get_staff_role(
            interaction.guild,
            config
        )

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