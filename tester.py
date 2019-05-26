from discord.ext import commands
import os
import sys

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


@client.event
async def on_ready():
    print(sys._getframe().f_code.co_name)


@client.event
async def on_raw_reaction_add(payload):
    print(
        sys._getframe().f_code.co_name,
        payload.message_id,
        payload.user_id,
        payload.channel_id,
        payload.guild_id,
        payload.emoji
    )


@client.event
async def on_raw_reaction_remove(payload):
    print(
        sys._getframe().f_code.co_name,
        payload.message_id,
        payload.user_id,
        payload.channel_id,
        payload.guild_id,
        payload.emoji
    )


@client.event
async def on_reaction_add(reaction, user):
    print(sys._getframe().f_code.co_name, reaction, user)


@client.event
async def on_reaction_remove(reaction, user):
    print(sys._getframe().f_code.co_name, reaction, user)


@client.event
async def on_voice_state_update(member, before, after):
    print(sys._getframe().f_code.co_name, member, before, after)


@client.event
async def on_member_join(member):
    print(sys._getframe().f_code.co_name, member)


@client.event
async def on_member_remove(member):
    print(sys._getframe().f_code.co_name, member)


@client.event
async def on_member_update(before, after):
    print(sys._getframe().f_code.co_name, before, after)


@client.event
async def on_message(message):
    print(sys._getframe().f_code.co_name, message)
    await client.process_commands(message)


@client.command()
async def test(ctx):
    pass


client.run(token)
