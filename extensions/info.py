import io
import discord
from time import time
from discord import app_commands
from discord.ext import commands
from daug.utils.dpyexcept import excepter
from typing import Literal

def get_members(guild):
    members = guild.members
    humans, bots = [], []
    for member in members:
        if member.bot:
            bots.append(member)
        else:
            humans.append(member)
    return members, humans, bots

def compose_channel_tree(guild):
    tree = []
    for category in guild.by_category():
        if category[0] is None:
            tree.append('C#')
        else:
            tree.append(f'C# {category[0].name}')
        for channel in category[1]:
            if isinstance(channel, discord.channel.TextChannel):
                tree.append(f'  T# {channel.name}')
            if isinstance(channel, discord.channel.VoiceChannel):
                tree.append(f'  V# {channel.name}')
            if isinstance(channel, discord.channel.ForumChannel):
                tree.append(f'  F# {channel.name}')
            if isinstance(channel, discord.channel.StageChannel):
                tree.append(f'  S# {channel.name}')
    return '\n'.join(tree)

class InformationCog(commands.GroupCog, group_name='情報'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='チャンネル数', description='現在のチャンネル数を表示します')
    @app_commands.rename(ephemeral='公開')
    @app_commands.describe(ephemeral='Botの応答を公開するか')
    @app_commands.guild_only()
    @excepter
    async def count_channel(self, interaction: discord.Interaction, ephemeral: Literal['公開', '非公開'] = '公開'):
        guild = interaction.guild
        embed = discord.Embed()
        embed.add_field(
            name=f'チャンネル数:{len(guild.channels)}',
            value=f'カテゴリ:{len(guild.categories)}\nテキスト:{len(guild.text_channels)}\nボイス:{len(guild.voice_channels)}\nフォーラム:{len(guild.forums)}\nステージ:{len(guild.stage_channels)}',
        )
        embed.add_field(
            name=f'スレッド数:{len(guild.threads)}',
            value=f'公開:{len([th for th in guild.threads if not th.is_private()])}\nプライベート:{len([th for th in guild.threads if th.is_private()])}')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='チャンネル構成', description='現在のチャンネル構成をファイル出力します')
    @app_commands.rename(ephemeral='公開')
    @app_commands.describe(ephemeral='Botの応答を公開するか')
    @app_commands.guild_only()
    @excepter
    async def tree_channel(self, interaction: discord.Interaction, ephemeral: Literal['公開', '非公開'] = '公開'):
        await interaction.response.send_message(
            file=discord.File(
                io.StringIO(compose_channel_tree(interaction.guild)),
                f'channels{int(time())}.txt',
            )
        )

    @app_commands.command(name='メンバー数', description='サーバー内のメンバー数と内訳を表示します')
    @app_commands.rename(ephemeral='公開')
    @app_commands.describe(ephemeral='Botの応答を公開するか')
    @app_commands.guild_only()
    @excepter
    async def listup_members(self, interaction: discord.Interaction, ephemeral: Literal['公開', '非公開'] = '公開'):
        guild = interaction.guild
        members, humans, bots = get_members(guild)
        embed = discord.Embed(
            title=f'メンバー数:{len(members)}',
            description=f'人間:{len(humans)}\nbot:{len(bots)}',
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='bot一覧', description='bot')
    @app_commands.rename(ephemeral='公開')
    @app_commands.describe(ephemeral='Botの応答を公開するか')
    @app_commands.guild_only()
    @excepter
    async def listup_bots(self, interaction: discord.Interaction, ephemeral: Literal['公開', '非公開'] = '公開'):
        guild = interaction.guild
        _, _, bots = get_members(guild)
        embed = discord.Embed(
            title='bot一覧',
            description=' '.join([bot.mention for bot in bots]),
        )
        offlines = [bot.mention for bot in bots if bot.status is discord.Status.offline]
        if len(offlines) > 0:
            embed.add_field(
                name='オフライン',
                value=' '.join(offlines),
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InformationCog(bot))
