import discord
import functions

def ping(client):
    @client.tree.command(name="ping", description="Returns latency time (ms)")
    async def ping(interaction: discord.Interaction):
        ping = int(client.latency * 1000)
        await interaction.response.send_message(f"Ping: {ping} ms! 🏓 ")

def help(client):
    @client.tree.command(name="help", description="List all commands, or get information about a specific command")
    async def help(interaction: discord.Interaction):
        embed=functions.help_embed()
        await interaction.response.send_message(embed=embed)

def mention(client):
    # When bot is mentioned
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # Check if the bot was mentioned in the message
        if client.user.mention in message.content:
            embed=functions.help_embed()
            await message.channel.send(embed=embed)