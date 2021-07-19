import os

import discord
from discord.ext import commands
from bot import unusualcog


from dotenv import load_dotenv
load_dotenv()


def getToken():
    token = os.getenv('DISCORD_TOKEN')
    return token


bot = commands.Bot(command_prefix=['bib.'])
bot.add_cog(unusualcog.Unusual(bot))



if __name__ == "__main__":
    bot.run(getToken())

