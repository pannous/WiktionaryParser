try:
	from .wiktionaryparser import WiktionaryParser
except :pass
from .wiktionaryimporter import query, search, titles, all
from .wiktionet import describe, word
