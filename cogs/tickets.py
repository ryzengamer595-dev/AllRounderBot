import discord
from discord import app_commands
from discord.ext import commands

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", emoji="🎫", style=discord.ButtonStyle.green, custom_id="allrounder:create_ticket")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            return await interaction.response.send_message(f"You already have {existing.mention}.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.id}",
            overwrites=overwrites,
            reason="Ticket created"
        )
        await channel.send(
            f"{interaction.user.mention} 🎫 Ticket created. Staff will help you here.",
            view=CloseTicketView()
        )
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.red, custom_id="allrounder:close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Closing ticket...")
        await interaction.channel.delete(reason="Ticket closed")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketView())
        bot.add_view(CloseTicketView())

    @app_commands.command(name="ticket", description="Create a ticket panel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket(self, interaction):
        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a private ticket.",
            color=discord.Color.blurple()
        )
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("Ticket panel sent.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
