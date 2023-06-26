import discord
from discord.ext.commands import Cog
from BackgroundPingu.bot.main import BackgroundPingu

class Tips(Cog):
    def __init__(self, bot: BackgroundPingu) -> None:
        super().__init__()
        self.bot = bot
        self.empty = "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"
    
    @discord.slash_command(name="fabric", description="A guide on how to install Fabric.")
    async def fabric(self, ctx: discord.ApplicationContext):
        text = "For your mods to work, you need to install Fabric Loader.\n" \
            "- For MultiMC and Prism Launcher, see the image how to do that.\n" \
            "- For official Minecraft Launcher, get the installer here: <https://fabricmc.net/use/installer>\n" \
            "Open the installer, select the Minecraft version you are playing and finish the installation.\n" \
            "Note: You do **NOT **need Fabric API, that is banned and you won't need it!\n" \
            "When you open your Minecraft launcher now it will show Fabric as an option. With that your mods will work.\n" \
            f"{self.empty}https://media.discordapp.net/attachments/433058639956410383/1099537217409531985/image.png"
        return await ctx.respond(text, ephemeral=True)

def setup(bot: BackgroundPingu):
    bot.add_cog(Tips(bot))
