"""Inspirational Discord Bot"""
# External Imports
import discord
# No Internal Imports

with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()

INSPIRE_BOT = discord.Client()
INSPIRE_BOT.run(TOKEN)
