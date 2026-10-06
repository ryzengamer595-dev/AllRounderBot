import discord
import asyncio
from discord import app_commands
from discord.ext import commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket 🎫", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        channel_name = f"ticket-{member.name}".lower()
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            return await interaction.response.send_message(f"❌ You already have a ticket open: {existing.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        await channel.send(f"👋 Hello {member.mention}, support team will assist you shortly!\nUse `/close` to close this ticket.")
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_ticket", description="Setup support ticket panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ticket_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a private support ticket.",
            color=discord.Color.green()
        )
        await interaction.response.send_message("Ticket panel created!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketView())

    @app_commands.command(name="close", description="Close the current ticket channel")
    async def close_slash(self, interaction: discord.Interaction):
        if "ticket-" in interaction.channel.name:
            await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ This command can only be used inside a ticket channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
