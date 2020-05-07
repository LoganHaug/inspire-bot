"""Inspirational Discord Bot"""
# External Imports
import discord
# No Internal Imports
# Grabs the bot token
with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()
# Starts the client
INSPIRE_BOT = discord.Client()
@INSPIRE_BOT.event
async def on_ready():
    print(f'{INSPIRE_BOT.user} connected to discord : )')
# Runs the client
INSPIRE_BOT.run(TOKEN)
