import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        
        if not category:
            category = await guild.create_category("Tickets")
            
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"❌ Aapka pehle se ek ticket khula hua hai: {existing_channel.mention}", ephemeral=True)
            return

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        embed = discord.Embed(
            title="Support Ticket",
            description=f"Welcome {interaction.user.mention}!\nStaff jald hi aapse judege. Neeche diye gaye buttons se ticket manage karein.",
            color=discord.Color.blue()
        )
        
        await channel.send(embed=embed, view=TicketControlView())
        await interaction.response.send_message(f"✅ Aapka ticket ban gaya hai: {channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket 5 seconds me band ho raha hai...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Custom title aur description ke sath ticket panel setup karein")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(title="Ticket Embed ka Title", description="Ticket Embed ka Description/Message")
    async def ticketsetup(self, interaction: discord.Interaction, title: str = "Support Center", description: str = "Kisi bhi madad ya query ke liye neeche diye gaye button par click karke ticket open karein!"):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Ticket panel successfully setup ho gaya!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))