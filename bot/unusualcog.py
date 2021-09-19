import os, sys
import traceback

from discord.ext import commands

from unusual import UnusualBot

import cutupargs

class Unusual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def makeParser(self):
        parser = cutupargs.getBotParser()
        parser.add_argument('bookPath', metavar="url", help="URL to text file to analyze")
        pos_group = parser.add_mutually_exclusive_group(required=True)
        pos_group.add_argument('-n', '--nouns', action='store_true', help="Analyze nouns.")
        pos_group.add_argument('-v', '--verbs', action='store_true', help="Analyze verbs.")
        pos_group.add_argument('-a', '--adjectives', action='store_true', help="Analyze adjectives.")

        
        return parser


    async def run(self, mode, args, channel):
        try: 
            c = Cmd()

            parser = self.makeParser()

            if not args:
                return "```" + parser.format_help() + "```"

            try:
                parsedArgs = parser.parse_args(args)
            except cutupargs.ArgException as ex:
                return "```" + parser.format_help() + "```\n" + ex.message

            c.count = parsedArgs.count
            if parsedArgs.count < 1:
                parsedArgs.count = 1
            if parsedArgs.count > 110:
                parsedArgs.count = 110

            parsedArgs.freqPath = os.getenv("FREQ_PATH")

            parsedArgs.tempDir = os.getenv("TEMP_DIR")

            parsedArgs.mode = mode

            parsedArgs.command = args

            u = UnusualBot(parsedArgs)

            if not u.hasTempFiles():
                await channel.send(f"Reading book at {parsedArgs.bookPath} for the first time. Please wait up to 10 minutes for results.")

            ret = u.run()

            return ret
        except Exception as ex:
            print(f"Error parsing book: {ex}", file=sys.stderr)
            traceback.print_tb(ex.__traceback__)
            return "Ran into an unexpected problem. Talk to Temmon, especially if it keeps happening."

    @commands.command(name="top")
    async def top(self, ctx, *args):
        await ctx.send(await self.run("top", args, ctx.channel))
    
    @commands.command(name="unusual") 
    async def unusual(self, ctx, *args):
        await ctx.send(await self.run("unusual", args, ctx.channel))

    @commands.command(name="percentage") 
    async def percentage(self, ctx, *args):
        await ctx.send(await self.run("percentage", args, ctx.channel))

    @commands.command(name="usage", aliases=["help"]) 
    async def usage(self, ctx, *args):
        commands = ["Commands are: ", "Bib.unusual", "Bib.top", "Bib.percentage", "Bib.help (shows this help message)"]
        example = ["Examples: ", "```Bib.unusual <url> -c 10 -v```",
                    "Runs the unusual command on verbs, with 10 results",
                    "```Bib.percentage <url> -n --abstract --strict -c 20```",
                    "Runs the percentage command on nouns, with 20 results. Only abstract nouns should be returned"]
        await ctx.send("\n".join(commands) + "\n\n```" + self.makeParser().format_help() + "```\n\n" + "\n".join(example))

class Cmd():
    pass

