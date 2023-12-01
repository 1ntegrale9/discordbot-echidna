import discord
from discord import app_commands
from discord.ext import commands
from utils.dpyexcept import excepter
from utils.dpylog import dpylogger


class ChannelOperationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='カテゴリ内の全チャンネル権限を同期', emoji='🔄', style=discord.ButtonStyle.green, custom_id='channel_operation:category_channels:sync')
    @excepter
    async def _sync_category_channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.resolved_permissions.administrator:
            await interaction.response.send_message('管理者専用機能です', ephemeral=True)
            return
        for channel in interaction.channel.category.channels:
            await channel.edit(sync_permissions=True)

    @discord.ui.button(label='カテゴリ内のチャンネルを全削除', emoji='🗑️', style=discord.ButtonStyle.red, custom_id='channel_operation:category_channels:delete')
    @excepter
    async def _delete_category_channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.resolved_permissions.administrator:
            await interaction.response.send_message('管理者専用機能です', ephemeral=True)
            return
        for channel in interaction.channel.category.channels:
            await channel.delete()


class ChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(ChannelOperationButtons())

    @app_commands.command(name='チャンネル管理パネル', description='チャンネルの各設定用のボタンを表示します')
    @app_commands.guild_only()
    @excepter
    @dpylogger
    async def _channel_manage_panel_command(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.manage_channels:
            await interaction.response.send_message('管理者専用機能です', ephemeral=True)
            return
        await interaction.response.send_message(view=ChannelOperationButtons())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelCog(bot))
