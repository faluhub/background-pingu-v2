import discord
from discord.ui import View, Button
from BackgroundPingu.core.issues import IssueBuilder

class Paginator(View):
    def __init__(self, messages: list[str], builder: IssueBuilder, post: discord.Message):
        super().__init__()
        self.timeout = 180
        self.disable_on_timeout = True
        self.page = 0
        self.uploaded = False
        self._messages = messages
        self.builder = builder
        self.post = post
        next_button = self.get_item("next")
        if isinstance(next_button, Button):
            next_button.disabled = len(self._messages) == 1
        upload_button = self.get_item("upload")
        if isinstance(upload_button, Button):
            upload_button.disabled = self.uploaded or self.builder.has("top_info", "uploaded_log") or self.builder.has("top_info", "uploaded_log_2") or self.builder.has("error", "leaked_session_id_token")
    
    async def edit_message(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.description = self._messages[self.page]
        embed.set_footer(text=f"Page {self.page + 1}/{len(self._messages)}")
        return await interaction.response.edit_message(content="", embeds=[embed], view=self)

    @discord.ui.button(emoji="⬅️", custom_id="back", disabled=True)
    async def back_callback(self, button: Button, interaction: discord.Interaction):
        if self.page == 0: return
        self.page -= 1
        button.disabled = self.page == 0
        next_button = self.get_item("next")
        if isinstance(next_button, Button):
            next_button.disabled = False
        return await self.edit_message(interaction)
    
    @discord.ui.button(emoji="➡️", custom_id="next", disabled=True)
    async def next_callback(self, button: Button, interaction: discord.Interaction):
        if self.page == len(self._messages) - 1: return
        self.page += 1
        button.disabled = self.page == len(self._messages) - 1
        back_button = self.get_item("back")
        if isinstance(back_button, Button):
            back_button.disabled = False
        return await self.edit_message(interaction)
    
    @discord.ui.button(label="Re-Upload Log", emoji="📜", custom_id="upload", disabled=True)
    async def upload_callback(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.post.author.id:
            return await interaction.response.send_message("You're not the original poster of this log.", ephemeral=True)
        includes, new_url = self.builder.log.upload()
        self.builder.top_info("uploaded_log" + ("_2" if includes else ""), new_url)
        self._messages = self.builder.build()
        button.disabled = True
        await self.edit_message(interaction)
        try: await self.post.delete(reason="Re-uploaded log.")
        except discord.Forbidden: pass
