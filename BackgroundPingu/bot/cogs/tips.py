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
            "Note: You do **NOT** need Fabric API, that is banned and you won't need it!\n" \
            "When you open your Minecraft launcher now it will show Fabric as an option. With that your mods will work."
        return await ctx.respond(text)

    @commands.slash_command(name="log", description="Shows how to send a log on MultiMC/Prism Launcher.")
    async def log(self, ctx: discord.ApplicationContext):
        text = "Please follow this image in order to send a log[:](https://cdn.discordapp.com/attachments/531598137790562305/575381000398569493/unknown.png)"
        return await ctx.respond(text)

    @commands.slash_command(name="mmclog", description="Shows how to send a log on MultiMC/Prism Launcher.")
    async def mmclog(self, ctx: discord.ApplicationContext):
        text = "Please follow this image in order to send a log[:](https://cdn.discordapp.com/attachments/531598137790562305/575381000398569493/unknown.png)"
        return await ctx.respond(text)

    @commands.slash_command(name="rankedfaq", description="Sends a link to the MCSR Ranked Tech Support FAQ document.")
    async def rankedfaq(self, ctx: discord.ApplicationContext):
        text = "You can find MCSR Ranked Tech Support FAQ document here: https://bit.ly/rankedfaq."
        return await ctx.respond(text)

    @commands.slash_command(name="ahk", description="Gives a guide to rebind keys using AutoHotkey.", aliases=["rebind"])
    async def ahk(self, ctx: discord.ApplicationContext):
        text = """To rebind keys, you can download AutoHotkey (<https://www.autohotkey.com/>, **make sure to get version 1.1**) and create a file with your desired key bindings. For instance, if you want to swap the keys "F3" and "r", you can create a file and name it *something*.ahk with the following content:
```ahk
#IfWinActive Minecraft
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
```ahk
#IfWinActive Minecraft
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
        return await ctx.respond("https://youtu.be/8Z0tk_Z24WA")

    @commands.slash_command(name="prism", description="Gives a link to download PrismLauncher.")
    async def prism(self, ctx: discord.ApplicationContext):
        return await ctx.respond("You can download the Prism Launcher here: https://prismlauncher.org/")

    @commands.slash_command(name="setup", description="Gives a link to a tutorial to setup Minecraft Speedrunning.")
    async def setup(self, ctx: discord.ApplicationContext):
        text = "https://youtu.be/VL8Syekw4Q0"
        return await ctx.respond(text)

    @commands.slash_command(name="fabricapi", description="Explains that Fabric API isn't legal.")
    async def fabricapi(self, ctx: discord.ApplicationContext):
        text = """⚠️ Fabric API is banned! __DO NOT USE IT!__ ⚠️ 
Fabric API is a mod separate from fabric loader, none of the allowed mods require it, and as such it is not allowed. If you have a fabric-api jar in .minecraft/mods you can just delete it, otherwise you're already fine"""
        return await ctx.respond(text)

    @commands.slash_command(name="1_16_1", description="Explains why using 1.16.1 is standard and recommended for Minecraft speedrunning.")
    async def one_sixteen_one(self, ctx: discord.ApplicationContext):
        text = "1.16.1 gives 4x more pearls and 3x more string from piglin barters on average compared to later versions. This, as well as not having piglin brutes, means that using 1.16.1 is standard and recommended for Minecraft speedrunning. You can play later versions if you wish (the category is 1.16+) but it will put you at a severe disadvantage. This only applies for RSG Any%, not SSG (which uses 1.16.5 for the current seed) or other category extensions."
        return await ctx.respond(text)

    @commands.slash_command(name="mapless", description="Gives links to mapless tutorials.")
    async def mapless(self, ctx: discord.ApplicationContext):
        text = """Penney's tutorial (beginner-friendly): <https://youtu.be/_dyD8ZwagDg>
TalkingMime's tutorial (more in-depth): <https://youtu.be/mes_PPlOJao>
MoleyG's tutorial (more updated): <https://youtu.be/ho1rwmooHRg>
pncake's tutorial (advanced): <https://youtu.be/ujZJw95h0nk>
Watch the 1st video for a rough overview, the 2nd and 3rd for more information and the 4th for a more advanced tutorial"""
        return await ctx.respond(text)

    @commands.slash_command(name="divine", description="Gives an infographic for nether fossil divine.")
    async def divine(self, ctx: discord.ApplicationContext):
        text = "https://cdn.discordapp.com/attachments/433058639956410383/897752137507946496/Screenshot_25.png"
        return await ctx.respond(text)

    @commands.slash_command(name="preemptivebug", description="Explains the preemptive bug.")
    async def preemptivebug(self, ctx: discord.ApplicationContext):
        text = "The pie chart may occasionally bug and give spikes significantly higher than expected. Assuming you're on Windows and your Minecraft is using an NVIDIA GPU, you can fix this by turning off \"Threaded optimization\" in the NVIDIA Control Panel, which you can access by right-clicking your Desktop[:](https://cdn.discordapp.com/attachments/433058639956410383/1166992505296920628/image.png)"
        return await ctx.respond(text)

    @commands.slash_command(name="julti", description="Gives a link to a Julti tutorial.")
    async def julti(self, ctx: discord.ApplicationContext):
        text = "https://youtu.be/QSEkkmwjhW8"
        return await ctx.respond(text)

    @commands.slash_command(name="modcheck", description="Gives a link to ModCheck.")
    async def modcheck(self, ctx: discord.ApplicationContext):
        text = "Application that helps install the allowed mods <https://github.com/tildejustin/modcheck/releases/latest>"
        return await ctx.respond(text)

    @commands.slash_command(name="1_16mods", description="Gives an explanation of 1.16 mods.")
    async def one_sixteen_mods(self, ctx: discord.ApplicationContext):
        text = """The allowed mods can be found and downloaded [**here**](<https://mods.tildejustin.dev/>)
AntiResourceReload and SetSpawn require Java 17 or newer[.](https://cdn.discordapp.com/attachments/433058639956410383/1184135653680742490/image.png) If you need help updating your Java version, do `/java`."""
        return await ctx.respond(text)

    @commands.slash_command(name="areessgee", description="Gives a link to AreEssGee.")
    async def areessgee(self, ctx: discord.ApplicationContext):
        text = """AreEssGee is a configurable artificial seed generator: <https://github.com/faluhub/AreEssGee>
Don't forget to check the info in the readme!"""
        return await ctx.respond(text)

    @commands.slash_command(name="peepopractice", description="Gives a link to PeepoPractice.")
    async def peepopractice(self, ctx: discord.ApplicationContext):
        text = """PeepoPractice is a Fabric 1.16.1 mod to practice splits of a Minecraft Any% speedrun. 
It includes a mapless split, bastion split, fortress split, postblind split, stronghold split, end split and more. 
Join the discord server linked in the github for updates and more info! 
Don't forget to check the FAQ in the readme! 
<https://github.com/faluhub/peepoPractice>"""
        return await ctx.respond(text)

    @commands.slash_command(name="allowedmods", description="Gives a link to allowed mods.")
    async def allowedmods(self, ctx: discord.ApplicationContext):
        text = """If you use Optifine (allowed only in pre-1.15), please read the [**detailed mod rules**](<http://bombch.us/DOOK>).
The allowed mods can be found and downloaded [**here**](<https://mods.tildejustin.dev/> ).
All other mods, including Fabric API, are banned[.](https://cdn.discordapp.com/attachments/433058639956410383/1184134775334764648/image.png)"""
        return await ctx.respond(text)

    @commands.slash_command(name="piedirectory", description="Gives the useful pie directories.")
    async def piedirectory(self, ctx: discord.ApplicationContext):
        text = """Common pie-chart directories:
Mapless / Preemptive: `root.gameRenderer.level.entities`
Village / Fortress: `root.tick.level.entities.blockEntities`"""
        return await ctx.respond(text)

    @commands.slash_command(name="standardsettings", description="Explains what StandardSettings is.")
    async def standardsettings(self, ctx: discord.ApplicationContext):
        text = """If your settings reset whenever you create a world, you are probably using StandardSettings <https://github.com/KingContaria/StandardSettings>
If you want to change the values that the settings reset to, click the link above and scroll down for instructions
If you don't want your settings to reset, remove StandardSettings from your mods folder"""
        return await ctx.respond(text)

    '''@commands.slash_command(name="modpack_list", description="Gives a list of MCSR modpacks.")
    async def modpack_list(self, ctx: discord.ApplicationContext):
        text = """### Modpacks for [PrismLauncher](<https://prismlauncher.org/download/>) / [MultiMC](<https://multimc.org/>) / [ATLauncher](<https://atlauncher.com/>)
Do `/modpack` for a tutorial on how to import them.
If the game crashes when it starts up, do `/java`.
If you're wondering why your settings keep resetting, do `/standardsettings`.
- **Full RSG 1.16.1 Pack (Includes all RSG mods, __RECOMMENDED__) (Requires Java 17+ (`/java`))**
  - Download: **[Windows](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.1-Windows-RSG.mrpack) | [macOS](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.1-OSX-RSG.mrpack) | [Linux](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.1-Linux-RSG.mrpack)**
- **Full SSG 1.16.5 Pack (Includes all SSG mods, __RECOMMENDED__) (Requires Java 17+ (`/java`))**
  - Download: **[Windows](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.5-Windows-SSG.mrpack) | [macOS](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.5-OSX-SSG.mrpack) | [Linux](https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.5-Linux-SSG.mrpack)**
- **Normal Ranked Pack (Includes basic mods for MCSR Ranked, __RECOMMENDED__)**
  - Download: **[Windows](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-Windows-1.16.1.mrpack) | [macOS](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-OSX-1.16.1.mrpack) | [Linux](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-Linux-1.16.1.mrpack)**
- **Full Ranked Pack (Requires __Java 17+__ (`/java`))**
  - Download: **[Windows](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-Windows-1.16.1-Pro.mrpack) | [macOS](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-OSX-1.16.1-Pro.mrpack) | [Linux](https://mods.tildejustin.dev/modpacks/v4/MCSRRanked-Linux-1.16.1-Pro.mrpack)**"""
        return await ctx.respond(text)

    @commands.slash_command(name="modpack", description="Gives instructions for setting up an RSG modpack instance.")
    async def modpack(self, ctx: discord.ApplicationContext):
        text = """Download [**MultiMC**](<https://multimc.org/>), extract it and launch `MultiMC.exe`. Click `Add instance > Import from zip`. Copy the link below that corresponds to your operating system, and paste it into the text field below `Import from zip`:
- Windows or Linux: <https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.1-Windows-RSG.mrpack>
- macOS: <https://mods.tildejustin.dev/modpacks/v4/MCSR-1.16.1-OSX-RSG.mrpack>
Click `OK` and the instance should be ready.
Demo: https://discord.com/channels/83066801105145856/405839885509984256/1127597457530945596
If this is your first time using MultiMC, go to `Settings > Java` and set the `Max memory allocation` to 2048 MB.
If the game crashes when it starts up, do `/java`. 
If you want a custom modpack, go [here](<https://mods.tildejustin.dev/?type=modpack>)"""
        return await ctx.respond(text)'''

    @commands.slash_command(name="practicemaps", description="Gives a list of practice maps.")
    async def practicemaps(self, ctx: discord.ApplicationContext):
        text = """*Consider getting [MapCheck](<https://github.com/cylorun/Map-Check/releases/latest>) to download multiple maps at once.*
[Bastions](<https://github.com/LlamaPag/bastion>)
[Blaze practice](<https://github.com/Semperzz/Blaze-Practice>)
[Buried treasure](<https://github.com/Mescht/BTPractice>)
[Crafting](<https://github.com/Semperzz/Crafting-Practice-v2>)
[One cycle / End practice](<https://github.com/ryguy2k4/ryguy2k4endpractice>)
[Overworld practice](<https://github.com/7rowl/OWPractice>)
[PeepoPractice, mod for all splits](<https://github.com/faluhub/peepoPractice>)
[Portals](<https://github.com/Semperzz/Portal-Practice>)
[Stronghold Trainer](<https://github.com/mjtb49/StrongholdTrainer>)
[Zero cycle](<https://zerocycle.repl.co/_zero_cycle_practice_astraf_nayoar.zip>)"""
        return await ctx.respond(text)

    @commands.slash_command(name="mapcheck", description="Gives a link to MapCheck.")
    async def mapcheck(self, ctx: discord.ApplicationContext):
        text = "Application that helps downloading minecraft speedrun practice maps: <https://github.com/cylorun/Map-Check/releases/latest>"
        return await ctx.respond(text)

    @commands.slash_command(name="boateye", description="Gives links to boat measurement guides.")
    async def boateye(self, ctx: discord.ApplicationContext):
        text = """[Full boat eye guide](https://docs.google.com/document/d/e/2PACX-1vTEq9UsoVef5Ed4OWCpw2xsvc7jZhWgK6gceCvhjz-i7DlsGj3p9SelEBclgvlsZ12tOQEYn4UC5X5n/pub) 
[Examples](<https://youtu.be/T2Wmhf4tNj4>)
Requires [Eye Zoom Macro](https://discord.com/channels/83066801105145856/405839885509984256/1143858381266894918)"""
        return await ctx.respond(text)

    @commands.slash_command(name="entity_culling", description="Explains how to turn off Entity Culling.")
    async def entity_culling(self, ctx: discord.ApplicationContext):
        text = "If your entity counter on F3 is `-1` or there isn't a `blockEntities` slice on the piechart in `root.gameRenderer.level.entities`, turn off `Entity Culling` in `Video Settings`."
        return await ctx.respond(text)

    @commands.slash_command(name="chunk_multidraw", description="Explains how to turn off Chunk Multidraw.")
    async def chunk_multidraw(self, ctx: discord.ApplicationContext):
        text = "If you're experiencing graphics related issues, such as water being invisible or blocks being inside you, try turning off `Chunk Multidraw` in `Video Settings` from the main screen."
        return await ctx.respond(text)

    @commands.slash_command(name="igpu", description="Gives a guide to get Minecraft to use the high-performance GPU.")
    async def igpu(self, ctx: discord.ApplicationContext):
        text = "If you are experiencing bad performance or graphics-related issues, it's possible that Minecraft is using your integrated GPU. To ensure that Minecraft uses your high-performance GPU, please follow this guide: <https://docs.google.com/document/d/1aPF1lyBAfPWyeHIH80F8JJw8rvvy6lRm0WJ2xxSrRh8/edit#heading=h.4oyoeerdwbr2>"
        return await ctx.respond(text)

    @commands.slash_command(name="desync", description="Gives a guide to ender eye desync for Minecraft speedruns.")
    async def desync(self, ctx: discord.ApplicationContext):
        text = "https://www.youtube.com/watch?v=uBqAeZMlEFQ"
        return await ctx.respond(text)

    # @commands.slash_command(name="", description="")
    # async def (self, ctx: discord.ApplicationContext):
    #     text = ""
    #     return await ctx.respond(text)

def setup(bot: BackgroundPingu):
    bot.add_cog(Tips(bot))
