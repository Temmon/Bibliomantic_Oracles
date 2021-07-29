# English text frequency analysis

This program will take text documents written in English, parse them to determine parts of speech, then order the nouns, verbs, and adjectives within it. From there, further analysis may be performed, such as specifying a text and identifying unusual words within that book, which are high in frequency in the book, but low in frequency in the full corpus.

Requires a current, modern version of Python. Developed on Python 3.8.

### To setup

1. Setup a virtual environment by running `python -m venv env`. The virtual environment is very helpful to keep your python installation healthy and robust. You should use it.

2. Activate the virtual environment by running `source env/bin/activate`

3. Install cython according to your OS. Search google for how to do this

4. Install the necessary libraries by running `pip install -r requirements.txt`

  a. If installing torch causes problems (the process may get killed on systems with small amounts of memory), install it by itself with `pip install torch --no-cache-dir`

5. Install libraries that spacy and nltk need to run.

  a. `python install -m spacy download en_core_web_sm`

  b. Install wordnet `python install_wordnet.py`

6. Create helpful empty directories: `mkdir output temp texts`

7. If you need to, deactivate the virtual environment by running `deactivate`

### To run

1. Activate your virtual environment: `source env/bin/activate`

2. For just the unusual words, run unusual.py

  a. It has detailed help instructions. I made empty output and temp directories to use if you want them.

  b. Sample command with default directories `python unusual.py frequencies/ texts/<path> -t temp -o output texts/<PATH TO BOOK>`

  c. `python unusual.py -h` to see the help.

Having a temp directory specified will save time by not rerunning the text when there's no changes to the book.

If there's an output directory, it will write the lists to the directory. Otherwise it'll print them to screen.

You can combine the flags for the different lists it will generate: eg -n for just nouns; -nv for nouns and verbs. By default it will run all 3. 

### To run the bot. 

1. Rename .env-shell to .env. 

2. Fill in the Discord token with your bot token in .env. 
  
  a. Follow Discord's instructions to generate a bot token if you don't have one.

3. If necessary, change the directories in .env.

4. NEVER COMMIT YOUR .ENV FILE WITH YOUR DISCORD TOKEN. Keep it a secret.

5. Run the bot with `python -m bot`

###Credits
Gutenberg download scripts were taken from the Project Gutenberg site.

Some scripts in tools.py (the commented ones...) are from https://towardsdatascience.com/text-classification-using-word-similarity-2f0c5fc9f365

I recommend you not download the Gutenberg corpus yourself (I'm not anymomre). Instead, there are a number of torrents. There's also Gutenberg dammit from https://github.com/aparrish/gutenberg-dammit, which I'm using now.


