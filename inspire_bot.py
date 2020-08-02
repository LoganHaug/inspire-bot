"""Inspirational Discord Bot"""
# External Imports
import discord
# Internal Imports
import message_parser
# Grabs the bot token
with open('token.txt', 'r') as token_file:
    TOKEN = token_file.read()
# Starts the client
INSPIRE_BOT = discord.Client()
@INSPIRE_BOT.event
async def on_ready():
    print(f'{INSPIRE_BOT.user} connected to discord : )')
@INSPIRE_BOT.event
async def on_message(message):
    user_id, message_text, mentions = message.author.id, message.content, message.mentions
    bot_message_text = message_parser.parse_message(message_text, user_id, mentions, INSPIRE_BOT)
    if bot_message_text is not None:
        channel = INSPIRE_BOT.get_channel(message.channel.id)
        await channel.send(bot_message_text)
# Runs the client
INSPIRE_BOT.run(TOKEN)
