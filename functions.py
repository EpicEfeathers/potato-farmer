import requests
from PIL import Image
from io import BytesIO
import time
import discord

def get_dominant_color(url):
        response = requests.get(url)
        im = Image.open(BytesIO(response.content))

        im1 = im.resize((1,1))
        color = im1.getpixel((0,0))
        color = (color[0] << 16) + (color[1] << 8) + color[2]
        return color

def format_large_number(number: int, shorten: bool):
    if shorten:
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}b"  # Billions
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}m"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}k"
        else:
            return number
    else:
        return f"{number:,}"
    
def create_timestamp(add_minutes):
    current_time = int(time.time())
    current_time += (add_minutes * 60)
    timestamp = f"<t:{current_time}:R>"
    
    return timestamp

def help_embed():
    embed=discord.Embed(title="Help",color=0x50C878)
    #embed.add_field(name="undefined", value="undefined", inline=False)

    return embed