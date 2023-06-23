from BackgroundPingu.bot import main
from BackgroundPingu import secrets
from BackgroundPingu.data import issues_sorter, mods_getter

if __name__ == "__main__":
    mods_getter.get_mods()
    issues_sorter.sort()
    main.BackgroundPingu().run(secrets.Discord.TOKEN)
