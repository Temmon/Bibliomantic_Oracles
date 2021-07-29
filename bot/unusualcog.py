import os
import traceback

from discord.ext import commands

from unusual import UnusualBot

def parseCount(args):
    ret = 10
    if len(args) > 1:
        try:
            ret = int(args[-1])
            if ret > 100:
                ret = 100
            elif ret < 1:
                ret = 1
        except ValueError:
            pass
    return ret

def getPos(args):
    if len(args) < 2:
        return "n"

    a = args[1].lower()
    if a == "v" or a == "a":
        return a

    return "n"

class Unusual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def run(self, mode, args):
        try: 
            c = Cmd()

            if not args:
                return "You need to send the path to a txt file to read."

            c.bookPath = args[0]

            c.pos = getPos(args)

            c.count = parseCount(args)

            c.freqPath = os.getenv("FREQ_PATH")

            c.tempDir = os.getenv("TEMP_DIR")

            c.mode = mode

            c.command = args

            u = UnusualBot(c)
            return u.run()
        except Exception as ex:
            print(f"Error parsing book: {ex}")
            traceback.print_tb(ex.__traceback__)
            return "Ran into an unexpected problem. Talk to Temmon, especially if it keeps happening."

    @commands.command(name="top")
    async def top(self, ctx, *args):
        await ctx.send(self.run("top", args))
    
    @commands.command(name="unusual") 
    async def unusual(self, ctx, *args):
        await ctx.send(self.run("unusual", args))

    @commands.command(name="percentage") 
    async def percentage(self, ctx, *args):
        await ctx.send(self.run("percentage", args))


class Cmd():
    pass

