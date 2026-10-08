import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

CONFIG_FILE = "ticket_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

class TicketControlView(discord.ui.View):
    def __init__(self, staff_role_id: int = None):
        super().__init__(timeout=None)
        self.staff_role_id = staff_role_id

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="🙋‍♂️", custom_id="claim_ticket_btn_v2")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.staff_role_id and not any(role.id == self.staff_role_id for role in interaction.user.roles):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Aapke paas is ticket ko claim karne ke liye Staff role nahi hai!", ephemeral=True)
                return

        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        button.style = discord.ButtonStyle.secondary
        
        embed = interaction.message.embeds[0]
        embed.add_field(name="🔒 Status", value=f"Claimed by {interaction.user.mention}", inline=False)
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"✅ Ticket claimed by {interaction.user.mention}!", ephemeral=False)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn_v2")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket 5 seconds me delete ho raha hai...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass

class TicketDynamicView(discord.ui.View):
    def __init__(self, options_data, staff_role_id):
        super().__init__(timeout=None)
        self.staff_role_id = staff_role_id
        
        for idx, opt in enumerate(options_data):
            label = opt.get("label", "Open")
            emoji = opt.get("emoji", "🎫")
            style_str = opt.get("style", "green")
            
            style = discord.ButtonStyle.green
            if style_str == "red": style = discord.ButtonStyle.danger
            elif style_str == "blue": style = discord.ButtonStyle.primary
            elif style_str == "grey": style = discord.ButtonStyle.secondary
            
            button = discord.ui.Button(
                label=f"Open ({label})",
                emoji=emoji,
                style=style,
                custom_id=f"ticket_opt_custom_{idx}"
            )
            button.callback = self.create_callback(opt)
            self.add_item(button)

    def create_callback(self, opt_info):
        async def callback(interaction: discord.Interaction):
            guild = interaction.guild
            category_name = opt_info.get("category", "Tickets")
            category = discord.utils.get(guild.categories, name=category_name)
            
            if not category:
                category = await guild.create_category(category_name)
                
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            if self.staff_role_id:
                staff_role = guild.get_role(self.staff_role_id)
                if staff_role:
                    overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            channel_name = f"ticket-{interaction.user.name.lower()}"
            existing = discord.utils.get(guild.text_channels, name=channel_name)
            if existing:
                await interaction.response.send_message(f"❌ Aapka pehle se ek ticket khula hua hai: {existing.mention}", ephemeral=True)
                return

            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            embed = discord.Embed(
                title=f"Support: {opt_info.get('label')}",
                description=f"Welcome {interaction.user.mention}!\n{opt_info.get('desc', 'Staff jald hi aapse judege.')}",
                color=discord.Color.blue()
            )
            
            await channel.send(embed=embed, view=TicketControlView(self.staff_role_id))
            await interaction.response.send_message(f"✅ Ticket ban gaya hai: {channel.mention}", ephemeral=True)
            
        return callback

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    ticket_group = app_commands.Group(name="ticket", description="Advanced Custom Ticket Management")

    @ticket_group.command(name="config", description="Panel ki Title, Description aur Staff Role set karein")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(title="Panel ka Title", description="Panel ki Guidelines / Description", staff_role="Staff Role")
    async def ticket_config(self, interaction: discord.Interaction, title: str, description: str, staff_role: discord.Role):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {}

        self.config[guild_id]["title"] = title
        self.config[guild_id]["description"] = description
        self.config[guild_id]["staff_role_id"] = staff_role.id
        if "options" not in self.config[guild_id]:
            self.config[guild_id]["options"] = []
            
        save_config(self.config)
        await interaction.response.send_message(f"✅ Config saved!\n**Title:** {title}\n**Staff Role:** {staff_role.mention}\nAb `/ticket addoption` se max 5 buttons add karein.", ephemeral=True)

    @ticket_group.command(name="addoption", description="Ticket panel me ek naya button/option add karein (Max 5)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        name="Button/Option Name (e.g. General Support)",
        description="Embed field me dikhane ke liye description",
        emoji="Button par lagane ke liye emoji",
        style="Button color: green, red, blue, grey"
    )
    @app_commands.choices(style=[
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Blue", value="blue"),
        app_commands.Choice(name="Grey", value="grey")
    ])
    async def ticket_addoption(self, interaction: discord.Interaction, name: str, description: str, emoji: str, style: str = "green"):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.config:
            self.config[guild_id] = {"options": []}

        if "options" not in self.config[guild_id]:
            self.config[guild_id]["options"] = []

        if len(self.config[guild_id]["options"]) >= 5:
            await interaction.response.send_message("❌ Aap maximum 5 hi options/buttons add kar sakte hain!", ephemeral=True)
            return

        self.config[guild_id]["options"].append({
            "label": name,
            "desc": description,
            "emoji": emoji,
            "style": style,
            "category": "Tickets"
        })
        save_config(self.config)
        await interaction.response.send_message(f"✅ Option **{name}** successfully add ho gaya! (Total: {len(self.config[guild_id]['options'])}/5)", ephemeral=True)

    @ticket_group.command(name="clearoptions", description="Saare custom options/buttons delete kar dein")
    @app_commands.default_permissions(administrator=True)
    async def ticket_clearoptions(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in self.config:
            self.config[guild_id]["options"] = []
            save_config(self.config)
        await interaction.response.send_message("🗑️ Saare options clear kar diye gaye hain.", ephemeral=True)

    @ticket_group.command(name="panel", description="Customize kiya hua final ticket panel channel me bhejein")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(banner_url="Optional Banner Image URL")
    async def ticket_panel(self, interaction: discord.Interaction, banner_url: str = None):
        guild_id = str(interaction.guild.id)
        data = self.config.get(guild_id)

        if not data or not data.get("options") or not data.get("staff_role_id"):
            await interaction.response.send_message("❌ Pehle `/ticket config` aur `/ticket addoption` set karein!", ephemeral=True)
            return

        embed = discord.Embed(
            title=data.get("title", "Support Center"),
            description=data.get("description", "Please select an option below."),
            color=discord.Color.blurple()
        )
        if banner_url:
            embed.set_image(url=banner_url)

        for opt in data["options"]:
            embed.add_field(name=f"{opt['emoji']} {opt['label']}", value=opt['desc'], inline=False)

        embed.set_footer(text=f"{interaction.guild.name} • Support Center")

        view = TicketDynamicView(data["options"], data["staff_role_id"])
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket panel successfully deploy ho gaya!", ephemeral=True)

    @ticket_group.command(name="add", description="Ticket me user add karein")
    @app_commands.describe(user="Jis user ko add karna hai")
    async def ticket_add(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ Ye command sirf ticket channels me kaam karegi!", ephemeral=True)
            return
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ Successfully added {user.mention} to this ticket.")

    @ticket_group.command(name="remove", description="Ticket se user remove karein")
    @app_commands.describe(user="Jis user ko remove karna hai")
    async def ticket_remove(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ Ye command sirf ticket channels me kaam karegi!", ephemeral=True)
            return
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(f"🔒 Successfully removed {user.mention} from this ticket.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))