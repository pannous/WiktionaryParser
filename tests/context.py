import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wiktionaryparser import WiktionaryParser
from wiktionaryimporter import query, search, titles