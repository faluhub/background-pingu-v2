import discord, re, traceback
from discord.ext.commands import Cog
from BackgroundPingu.bot.main import BackgroundPingu
from BackgroundPingu.core import parser, issues
from BackgroundPingu.bot.ui import views

class Core(Cog):
    def __init__(self, bot: BackgroundPingu) -> None:
        super().__init__()
        self.bot = bot

    @Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.id == self.bot.user.id: return

        link_pattern = r"https:\/\/paste\.ee\/p\/\w+|https:\/\/mclo\.gs\/\w+|https?:\/\/[\w\/.]+\.(?:txt|log)"
        matches = re.findall(link_pattern, msg.content)
        if len(msg.attachments) > 0:
            for attachment in msg.attachments:
                matches.append(attachment.url)
        for match in matches:
            log = parser.Log.from_link(match)
            if not log is None:
                try:
                    results = issues.IssueChecker(self.bot, log).check()
                    if results.has_values():
                        messages = results.build()
                        embed = discord.Embed(
                            title=f"{results.amount} Issue{'s' if results.amount > 1 else ''} Found:",
                            description=messages[0],
                            color=self.bot.color
                        )
                        return await msg.reply(embed=embed, view=views.Paginator(messages))
                except Exception as e:
                    error = "".join(traceback.format_exception(e))
                    return await msg.reply(f"```\n{error}\n```\n<@810863994985250836>, <@695658634436411404> :bug:")

def setup(bot: BackgroundPingu):
    bot.add_cog(Core(bot))
