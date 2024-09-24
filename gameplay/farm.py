import discord

def plant(client):
    @client.tree.command(name="plant", description="Plant a crop of potatoes")
    async def plant(interaction: discord.Interaction):
        ping = int(client.latency * 1000)
        await interaction.response.send_message(f"Ping: {ping} ms! 🏓 ")