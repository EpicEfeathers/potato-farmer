import discord

def ping(client):
    @client.tree.command(name="ping", description="Returns latency time (ms)")
    async def ping(interaction: discord.Interaction):
        ping = int(client.latency * 1000)
        await interaction.response.send_message(f"Ping: {ping} ms! 🏓 ")