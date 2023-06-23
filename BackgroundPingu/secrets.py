import os, dotenv

dotenv.load_dotenv()

class Discord:
    TOKEN = os.getenv("DISCORD_TOKEN")
