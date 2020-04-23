from discord.ext.commands import Bot

token = open("token").read()


class WPSBot(Bot):
    pass


bot = WPSBot("!")

bot.load_extension("extensions.wps_commands")
bot.run(token)
