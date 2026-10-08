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

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="🙋‍♂️", custom_id="claim_ticket_btn")
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

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
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
            label = opt.get("label", "Create Ticket")
            emoji = opt.get("emoji", "🎫")
            
            button = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.green,
                custom_id=f"ticket_opt_{idx}"
            )
            button.callback = self.create_callback(opt)
            self.add_item(button)

    def create_callback(self, opt_info):
        async def callback(interaction: discord.Interaction):
            guild = interaction.guild
            category = discord.utils.get(guild.categories, name="Tickets")
            
            if not category:
                category = await guild.create_category("Tickets")
                
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
                title="Support Ticket",
                description=f"Welcome {interaction.user.mention}!\nStaff jald hi aapse judege.",
                color=discord.Color.blue()
            )
            
            await channel.send(embed=embed, view=TicketControlView(self.staff_role_id))
            await interaction.response.send_message(f"✅ Ticket ban gaya hai: {channel.mention}", ephemeral=True)
            
        return callback

class TicketSetupModal(discord.ui.Modal, title="Ticket Panel Setup Menu"):
    def __init__(self, staff_role):
        super().__init__()
        self.staff_role = staff_role

    panel_title = discord.ui.TextInput(label="Panel Title", placeholder="Support Center", default="Support Center", required=True)
    panel_desc = discord.ui.TextInput(label="Panel Description / Guidelines", style=discord.TextStyle.paragraph, placeholder="Yahan guidelines ya description likhein...", default="Kisi bhi madad ke liye button par click karein!", required=True)
    btn_text = discord.ui.TextInput(label="Button Text", placeholder="Create Ticket", default="Create Ticket", required=True)
    btn_emoji = discord.ui.TextInput(label="Button Emoji", placeholder="🎫", default="🎫", required=True)
    banner = discord.ui.TextInput(label="Banner Image URL (Optional)", placeholder="https://...", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        config = load_config()
        if guild_id not in config:
            config[guild_id] = {}

        config[guild_id]["staff_role_id"] = self.staff_role.id
        config[guild_id]["title"] = self.panel_title.value
        config[guild_id]["description"] = self.panel_desc.value
        
        options = [{
            "label": self.btn_text.value,
            "emoji": self.btn_emoji.value
        }]
        config[guild_id]["options"] = options
        save_config(config)

        embed = discord.Embed(
            title=self.panel_title.value,
            description=self.panel_desc.value,
            color=discord.Color.blurple()
        )
        if self.banner.value:
            embed.set_image(url=self.banner.value)
        embed.set_footer(text=f"{interaction.guild.name} • Support Center")

        view = TicketDynamicView(options, self.staff_role.id)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket panel successfully deploy ho gaya!", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Menu kholkar ticket panel setup karein")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(staff_role="Staff Role jise ticket ka access milega")
    async def ticketsetup(self, interaction: discord.Interaction, staff_role: discord.Role):
        await interaction.response.send_modal(TicketSetupModal(staff_role))

    @app_commands.command(name="ticketadd", description="Ticket me user add karein")
    @app_commands.describe(user="Jis user ko add karna hai")
    async def ticket_add(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ Ye command sirf ticket channels me kaam karegi!", ephemeral=True)
            return
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ Successfully added {user.mention} to this ticket.")

    @app_commands.command(name="ticketremove", description="Ticket se user remove karein")
    @app_commands.describe(user="Jis user ko remove karna hai")
    async def ticket_remove(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("❌ Ye command sirf ticket channels me kaam karegi!", ephemeral=True)
            return
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(f"🔒 Successfully removed {user.mention} from this ticket.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))