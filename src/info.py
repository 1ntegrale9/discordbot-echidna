from discord import Embed

helps = {
    '/randid':
        'DiscordのIDのダミーを生成します',
    '/randtoken':
        'Discordのアクセストークンのダミーを生成します',
    '/randcolor':
        '10進数のカラーコードをランダム生成します',
    '/role':
        'サーバーの役職一覧を表示します',
    '/member':
        'サーバーの人数を表示します',
    '/help':
        'コマンドの一覧と詳細を表示します',
}


def get_help(bot):
    embed = Embed(
        title=bot.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='powered by discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=bot.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
    return embed
