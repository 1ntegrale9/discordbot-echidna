import discord
from discord.ext import commands
from echidna.daug import get_default_embed


def get_role_names(roles):
    return sorted([role.name for role in roles if not role.is_default()])


class TwistWerewolf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id = 307721817563594753
        self.category_music_id = 548752809965781013
        self.category_private_id = 361479341256998914
        self.category_free_id = 548777809343021056

    async def cog_check(self, ctx):
        return ctx.guild.id == self.id

    def can_rename(self, category_id):
        return category_id in [
            self.category_private_id,
            self.category_free_id,
        ]

    async def toggle_channel_readable(self, member, channel, can_read):
        await discord.utils.get(
            iterable=member.guild.text_channels,
            name=channel.name
        ).set_permissions(
            target=member,
            read_messages=can_read
        )

    async def invite(self, message):
        members = message.mentions
        if not bool(members):
            await message.channel.send('誰を招待すればいいの？')
            return
        channel = message.channel_mentions
        if len(channel) == 0:
            channel = message.channel
        elif len(channel) == 1:
            channel = channel[0]
            if not message.author.permissions_in(channel).read_messages:
                await message.channel.send('君には招待する権利がないみたい')
                return
        else:
            await message.channel.send('チャンネルを1つだけ指定してね！')
            return
        for member in members:
            await channel.set_permissions(member, read_messages=True)
            description = f'{member.mention} を招待したよ'
            embed = get_default_embed(description)
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(embed=embed)

    async def kick(self, message):
        members = message.mentions
        if not bool(members):
            await message.channel.send('誰を追放すればいいの？')
            return
        for member in members:
            await message.channel.set_permissions(member, read_messages=False)
            description = f'{member.mention} を追放したよ'
            embed = get_default_embed(description)
            embed.set_thumbnail(url=member.avatar_url)
            await message.channel.send(embed=embed)

    async def age(self, message):
        category = message.channel.category
        if category and category.id != self.category_free_id:
            return
        await message.channel.edit(
            category=category,
            position=0
        )

    async def create_channel(self, message):
        n = len('new:')
        await message.guild.create_text_channel(
            name=message.content[n:],
            category=message.guild.get_channel(self.category_free_id)
        )

    async def create_private_channel(self, message):
        n = len('private:')
        await message.guild.create_text_channel(
            name=message.content[n:],
            category=message.guild.get_channel(self.category_private_id),
            overwrites={
                message.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False
                ),
                message.author: discord.PermissionOverwrite(read_messages=True),
            }
        )

    async def rename(self, message):
        if not self.can_rename(message.channel.category_id):
            return
        n = len('name:')
        await message.channel.edit(name=message.content[n:])
        await message.delete()

    async def overwrite_topic(self, message):
        if not self.can_rename(message.channel.category_id):
            return
        n = len('topic:')
        await message.channel.edit(topic=message.content[n:])
        await message.delete()

    @commands.command()
    @commands.guild_only()
    async def role(self, ctx, *args):
        async def set_roles(message):
            add, rm, pd, nt = [], [], [], []
            role_names = [role.name.lower() for role in message.guild.roles]
            for role_name in message.content.split()[1:]:
                if role_name.lower() in role_names:
                    index = role_names.index(role_name.lower())
                    role = message.guild.roles[index]
                    if role in message.author.roles:
                        rm.append(role)
                    elif role.permissions.administrator:
                        pd.append(role)
                    else:
                        add.append(role)
                else:
                    nt.append(role_name)
            msg = ''
            if add:
                await message.author.add_roles(*add)
                rolenames = ', '.join([r.name for r in add])
                msg = f'{msg}\n役職 {rolenames} を付与しました'
            if rm:
                await message.author.remove_roles(*rm)
                rolenames = ', '.join([r.name for r in rm])
                msg = f'{msg}\n役職 {rolenames} を解除しました'
            if pd:
                rolenames = ', '.join([r.name for r in pd])
                msg = f'{msg}\n役職 {rolenames} は追加できません'
            if nt:
                rolenames = (', '.join(nt))
                msg = f'{msg}\n役職 {rolenames} は存在しません'
            return msg
        if args:
            msg = await set_roles(ctx.message)
            await ctx.send(msg)
        else:
            role_names = get_role_names(ctx.guild.roles)
            text = 'このサーバーにある役職は以下の通りです\n' + \
                ', '.join(role_names) if role_names else '役職がありません'
            await ctx.send(text)

    @commands.command()
    @commands.guild_only()
    async def role_self(self, ctx):
        role_names = get_role_names(ctx.author.roles)
        text = ', '.join(role_names) if role_names else '役職が設定されていません'
        await ctx.send(text)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id != self.id:
            return
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.channel.TextChannel):
            return
        if not bool(message.content):
            return
        await self.age(message)
        if message.content.startswith('name:'):
            await self.rename(message)
        if message.content.startswith('new:'):
            await self.create_channel(message)
        if message.content.startswith('private:'):
            await self.create_private_channel(message)
        if message.content.startswith('topic:'):
            await self.overwrite_topic(message)
        if message.content.split()[0] == '招待':
            await self.invite(message)
        if message.content.split()[0] == '追放':
            await self.kick(message)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != self.id:
            return
        if member.bot:
            return
        b, a = before.channel, after.channel
        if not ((b is None) ^ (a is None) and (b or a).category_id == self.category_music_id):
            return
        await self.toggle_channel_readable(
            member=member,
            channel=(b or a),
            can_read=bool(a)
        )


def setup(bot):
    bot.add_cog(TwistWerewolf(bot))
