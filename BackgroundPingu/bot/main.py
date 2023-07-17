import discord, os, json
from datetime import datetime
from discord import AutoShardedBot as asb

class BackgroundPingu(asb):
    def __init__(self):
        self.start_time = datetime.utcnow()

        with open("./BackgroundPingu/data/issues.json", "r") as f:
            self.strings = json.load(f)
        with open("./BackgroundPingu/data/mods.json", "r") as f:
            self.mods = json.load(f)

        self.cog_blacklist = []
        self.cog_folder_blacklist = ["__pycache__"]
        self.path = "./BackgroundPingu/bot/cogs"

        self.color = 0xFFC113

        super().__init__(
            intents=discord.Intents.all(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            owner_ids=[810863994985250836, 695658634436411404],
            debug_guilds=[1018128160962904114]
        )

        print("\nLoading cogs..."),
        self.load_cogs()

    def load_cogs(self, folder=None):
        if not folder is None: self.path = os.path.join(self.path, folder)
        formatted_path = self.path.strip("./").replace("/", ".").replace("\\", ".")

        for file in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path, file)):
                if not file in self.cog_blacklist:
                    try:
                        self.load_extension(f"{formatted_path}.{file[:-3]}")
                        print(f"  Loaded '{file}'")
                    except Exception as e: print(e)
            else:
                if not file in self.cog_folder_blacklist:
                    self.load_cogs(file)
    
    async def on_connect(self):
        print("Registering commands...")
        await self.sync_commands()
        await self.register_commands()
        print("\nConnected")

    async def on_ready(self):
        return print(f"Ready, took {(datetime.utcnow() - self.start_time).seconds} seconds.")

if __name__ == "__main__":
    exit("The bot cannot be run directly from the bot file.")
