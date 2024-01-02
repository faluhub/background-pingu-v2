import discord
from discord import commands
from discord.ext.commands import Cog
from BackgroundPingu.bot.main import BackgroundPingu

class Tips(Cog):
    def __init__(self, bot: BackgroundPingu) -> None:
        super().__init__()
        self.bot = bot
    
    @commands.slash_command(name="fabric", description="A guide on how to install Fabric.")
    async def fabric(self, ctx: discord.ApplicationContext):
        text = "For your mods to work, you need to install Fabric Loader.\n" \
            "- For MultiMC and Prism Launcher, see the image how to do that[.](https://media.discordapp.net/attachments/433058639956410383/1099537217409531985/image.png)\n" \
            "- For official Minecraft Launcher, get the installer here: <https://fabricmc.net/use/installer/>\n" \
            "Open the installer, select the Minecraft version you are playing and finish the installation.\n" \
            "Note: You do **NOT **need Fabric API, that is banned and you won't need it!\n" \
            "When you open your Minecraft launcher now it will show Fabric as an option. With that your mods will work."
        return await ctx.respond(text, ephemeral=True)

    @commands.slash_command(name="log", description="Shows how to send a log on MultiMC/Prism Launcher.")
    async def log(self, ctx: discord.ApplicationContext):
        text = "Please follow this image in order to send a log[:](https://cdn.discordapp.com/attachments/531598137790562305/575381000398569493/unknown.png)"
        return await ctx.respond(text)

    @commands.slash_command(name="rankedfaq", description="Sends a link to the MCSR Ranked Tech Support FAQ document.")
    async def rankedfaq(self, ctx: discord.ApplicationContext):
        text = "You can find MCSR Ranked Tech Support FAQ document here: https://bit.ly/rankedfaq."
        return await ctx.respond(text)

    @commands.slash_command(name="ahk", description="Gives a guide to rebind keys using AutoHotkey.", aliases=["rebind"])
    async def ahk(self, ctx: discord.ApplicationContext):
        text = """To rebind keys, you can download AutoHotkey (<https://www.autohotkey.com/>, **make sure to get version 1.1**) and create a file with your desired key bindings. For instance, if you want to swap the keys "F3" and "r", you can create a file and name it *something*.ahk with the following content:
```#IfWinActive Minecraft
*F3::r
*r::F3```Launch the file, and the input of keys "F3" and "r" will be swapped (which means pressing "r" will open the debug menu). You can customize the key bindings as desired. <https://www.autohotkey.com/docs/v1/KeyList.htm> 

**Rebind Rules**
You may remap keys using external programs, but:
• Each game input may have only one key, and each key may cause only one game input
• F3 shortcuts (such as F3+C, Shift+F3, etc.) can't be bound to a single button
• Inputs must be buttons - no scrolling the scroll-wheel or similar
• Rebinding "Attack/Destroy" or "Use Item/Place Block" to a keyboard button in order to abuse as an autoclicker is not allowed"""
        return await ctx.respond(text)

    @commands.slash_command(name="rebind", description="Gives a guide to rebind keys using AutoHotkey.", aliases=["rebind"])
    async def rebind(self, ctx: discord.ApplicationContext):
        text = """To rebind keys, you can download AutoHotkey (<https://www.autohotkey.com/>, **make sure to get version 1.1**) and create a file with your desired key bindings. For instance, if you want to swap the keys "F3" and "r", you can create a file and name it *something*.ahk with the following content:
```#IfWinActive Minecraft
*F3::r
*r::F3```Launch the file, and the input of keys "F3" and "r" will be swapped (which means pressing "r" will open the debug menu).
You can customize the key bindings as desired, see this for help: <https://www.autohotkey.com/docs/v1/KeyList.htm> 

**Rebind Rules**
You may remap keys using external programs, but:
• Each game input may have only one key, and each key may cause only one game input
• F3 shortcuts (such as F3+C, Shift+F3, etc.) can't be bound to a single button
• Inputs must be buttons - no scrolling the scroll-wheel or similar
• Rebinding "Attack/Destroy" or "Use Item/Place Block" to a keyboard button in order to abuse as an autoclicker is not allowed"""
        return await ctx.respond(text)

    @commands.slash_command(name="new", description="Provides a comprehensive guide to start learning speedrunning.")
    async def new(self, ctx: discord.ApplicationContext):
        text = """The most popular category/version to run is 1.16.1 any% random seed glitchless, so we're assuming you're planning to run this category.

Watch this video <https://youtu.be/VL8Syekw4Q0> to set up minecraft for speedrunning. It goes through everything from setting up MultiMC to installing mods and practice maps, so it's highly recommended to watch this first.

The most important things to learn when starting out are bastion routes and one-cycling. Watch these videos <https://www.youtube.com/playlist?list=PL7Q35RXRsOR-udeKzwlYGJd0ZrvGJ0fwu> for introductory bastion routes and this video <https://youtu.be/JaVyuTyDxxs> for one-cycling.

In general, it's a good idea to watch top runs and top runners' streams to get a feel of how a speedrun goes. Here's a more comprehensive document <https://docs.google.com/document/d/1zDC0n38EhvcMaXVFVeZwONszmdXonXlFO1rBXqvhxE4/edit?usp=sharing>, but since it covers a lot of strategies it may seem overwhelming at first, so take it easy."""
        return await ctx.respond(text)

    @commands.slash_command(name="jarfix", description="Gives a link to Jarfix.")
    async def jarfix(self, ctx: discord.ApplicationContext):
        text = "Jarfix fixes the jar file association on Windows: https://johann.loefflmann.net/en/software/jarfix/index.html"
        return await ctx.respond(text)

    @commands.slash_command(name="java", description="Gives a guide to update Java.")
    async def java(self, ctx: discord.ApplicationContext):
        text = """* You can install the latest version of Java [**here**](<https://adoptium.net/temurin/releases/>). Download the .msi file if you're on Windows, download the .pkg file if you're on macOS.
* After installing Java, follow the steps in the image below (assuming you're using MultiMC or Prism launcher)[:](https://cdn.discordapp.com/attachments/433058639956410383/1172533931485175879/image.png)
 * On Prism, also make sure to disable the Java compatibility check in Settings > Java.
* We do not recommend using the official Minecraft launcher since it is [tedious](<https://bit.ly/updatejavamc>) to switch Java versions. Watch [**this video**](<https://youtu.be/VL8Syekw4Q0>) to set up MultiMC for speedrunning."""
        return await ctx.respond(text)

    @commands.slash_command(name="ninjabrainbot", description="Gives a guide to using Ninjabrain Bot.")
    async def ninjabrainbot(self, ctx: discord.ApplicationContext):
        text = "https://youtu.be/8Z0tk_Z24WA"
        return await ctx.respond(text)

    @commands.slash_command(name="prism", description="Gives a link to download PrismLauncher.")
    async def prism(self, ctx: discord.ApplicationContext):
        text = "You can download the Prism Launcher here: https://prismlauncher.org/"
        return await ctx.respond(text)

def setup(bot: BackgroundPingu):
    bot.add_cog(Tips(bot))
