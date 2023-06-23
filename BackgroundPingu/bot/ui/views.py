import discord
from discord.ui import View, Button
from discord.ui.item import Item

class Paginator(View):
    def __init__(self, messages: list[str]):
        super().__init__()
        self.timeout = 180
        self.disable_on_timeout = True
        self.page = 0
        self._messages = messages
        next_button = self.get_item("next")
        if isinstance(next_button, Button):
            next_button.disabled = len(self._messages) == 1
    
    async def edit_message(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.description = self._messages[self.page]
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
