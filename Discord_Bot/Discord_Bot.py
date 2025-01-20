import discord
from discord import app_commands
from discord.ext import commands
import json
import requests
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


def has_role(role_name: str):
    async def predicate(interaction: discord.Interaction):
        if any(role.name == role_name for role in interaction.user.roles):
            return True
        await interaction.response.send_message(embed=discord.Embed(title="You do not have permission to use this command", color=discord.Color.red()), ephemeral=True)
        return False
    return app_commands.check(predicate)



@bot.tree.command(name="add")
@has_role('List Editor')
async def add(interaction: discord.Interaction, name: str, area: str, *, reason: str):
    response = requests.post(
        "http://localhost:3000/addUser",
        json={"username": name, "area": area, "reason": reason, "addedBy": str(interaction.user)}
    )

    if response.status_code == 200:
        embed = discord.Embed(title=f"`{name}` was added to the list", color=discord.Color.green())
        embed.add_field(name="Area", value=f"{area}", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        await interaction.response.send_message(embed=embed)
    
    elif response.status_code == 400:
        embed = discord.Embed(title="Failed to add user: Missing fields", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    elif response.status_code == 409:
        embed = discord.Embed(title=f"Failed to add user: `{name}` is already on the list", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    else:
        embed = discord.Embed(title="Failed to add user: Server error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)


@add.error
async def add_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(title="You do not have permission to use this command", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="check")
async def check(interaction: discord.Interaction, name: str):
    response = requests.get(
        "http://localhost:3000/checkUser",
        params={"username": name}
    )

    if response.status_code == 200:
        player = response.json()
        embed = discord.Embed(title=f"`{player['username']}` was found on the list", color=discord.Color.blue())
        embed.add_field(name="Area", value=f"{player['area']}", inline=False)
        embed.add_field(name="Reason", value=f"{player['reason']}", inline=False)
        embed.add_field(name="Added by", value=f"{player['addedBy']}", inline=False)
        await interaction.response.send_message(embed=embed)
    elif response.status_code == 404:
        embed = discord.Embed(title=f"`{name}` is not a shitter    *yet...*", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Failed to check user: Server error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)



@bot.tree.command(name="list")
async def list(interaction: discord.Interaction):
    response = requests.get(
        "http://localhost:3000/findAll"
    )

    if response.status_code == 200:
        player_list = response.json()
        embed = discord.Embed(title="Shitter List", color=discord.Color.blue())
        for player in player_list:
            player_name = f"`{player['username']}`"
            player_area = player['area']
            player_reason = player['reason']
            embed.add_field(
                name=player_name,
                value=f"__Area__: {player_area}\n__Reason__: {player_reason}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)
    elif response.status_code == 404:
        embed = discord.Embed(title="The shitter list is empty", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Failed to get the list: Server error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)


@bot.tree.command(name="remove")
@has_role('List Editor')
async def remove(interaction: discord.Interaction, name: str, *, reason: str = "No Reason Provided"):
    response = requests.delete(
        "http://localhost:3000/deleteUser",
        json={"username": name}
    )

    if response.status_code == 200:
        embed = discord.Embed(title=f"`{name}` was removed from the list", color=discord.Color.orange())
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        await interaction.response.send_message(embed=embed)
    
    elif response.status_code == 404:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"`{name}` is not on the shitter list", value="", inline=False)
        await interaction.response.send_message(embed=embed)

    else:
        embed = discord.Embed(title="Failed to remove user: Server error", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

@remove.error
async def remove_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(title="You do not have permission to use this command", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

BOT_TOKEN = os.getenv("BOT_SECRET")

bot.run(BOT_TOKEN)