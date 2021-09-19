import argparse
from argparse import SUPPRESS

class ArgException(Exception):
    def __init__(self, message):
        self.message = message

def getParser(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(description='Find the most unusual words in a book.')
    
    parser.add_argument('--count', '-c', type=int, help="Number of results in each list. Defaults to 10.", default=10)
    parser.add_argument('--abstract', action='store_true', default=False, help="Show abstract nouns.")
    parser.add_argument('--physical', action='store_true', default=False, help="Show nouns that are physical objects.")
    parser.add_argument('--strict', action='store_true', default=False, help="If abstract or physical are set, only select nouns that meet that category and not the other one.")
    parser.add_argument('--people', action='store_true', default=False, help="Only show nouns that are related to people.")

    return parser

def getBotParser():
    class BotParser(argparse.ArgumentParser):
        def error(self, message):
            raise ArgException(message)

    return getParser(BotParser(description='Find the most unusual words in a book.', add_help=False, usage=SUPPRESS))

