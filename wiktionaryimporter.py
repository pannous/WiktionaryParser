#!/usr/bin/env python3
import bz2
import xml
import xml.sax
import sqlite3
from os.path import exists, isfile

url = 'https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2'

conn = sqlite3.connect('wiktionary.sqlite')

# The database will be saved where your 'py' file is saved


def prepare_database(drop= False):
	c = conn.cursor()
	if drop:
		c.execute('''DROP TABLE IF EXISTS wiktionary''')
	c.execute('''
	CREATE TABLE IF NOT EXISTS wiktionary(
		[iid] INTEGER PRIMARY KEY,
		[title] text, 
		[content] text,
		[id] integer, 
		[date] date
	)
	''')
	c.execute('''
		CREATE INDEX title_index ON wiktionary (title);
	''')
	conn.commit()
	
def prepare_search_index():
	print(' building full search index')
	c = conn.cursor()
	#VIRTUAL
	c.execute('''
		CREATE VIRTUAL TABLE search 
		USING FTS5(title, content);
	''')
	c.execute('''INSERT OR IGNORE INTO search(title, content) SELECT title, content FROM wiktionary;''') 
	if 0 > 1:  #test
		c.execute('''
		INSERT INTO wiktionary(title, content) VALUES
			('test','ok ')
		''')
	conn.commit()

def search(phrase, limit= 1000000):
	c = conn.cursor()
	phrase = phrase. replace('|','+') #Todo right
	phrase = phrase. replace(':','+') 
	#prepare_search_index()
	c.execute('''
		SELECT * 
		FROM search
		WHERE content MATCH '%s' LIMIT %d;
	'''%( phrase, limit))
	results = c.fetchall()
	return [r[0] for r in results]

class StreamHandler(xml.sax.handler.ContentHandler):
	count = 0
	lastEntry = {}
	lastName = None

	def startElement(self, name, attrs):
		#help(attrs)
		self.lastName = name
		if name == 'page':
			self.lastEntry = {'page': {}}
		elif self.lastEntry:
			self.lastEntry[name] = {'attrs': attrs.__dict__['_attrs'], 'content': ''}

	def endElement(self, name):
		if name == 'root':  #or self.count > 100000:
			raise StopIteration
		if name == 'page':
			title = self.lastEntry['title']['content']
			text = self.lastEntry['text']['content']
			#print(title)
			if not "Wik" in title and not "Index" in title:  #Wiktionary wikcinario
				c = conn.cursor()
				insertion = 'INSERT INTO wiktionary(title, content) VALUES (?,?)'
				c.execute(insertion, (title, text))
				if self.count % 1000 == 0:
					conn.commit()
					print("documents done: %d\r" % self.count)
				self.count = self.count + 1
			self.lastEntry = None

	def characters(self, content):
		if self.lastName == 'page':
			return
		#if (self.lastName == 'title') and content.strip():
		#	print(content)
		if self.lastEntry:
			self.lastEntry[self.lastName]['content'] += content.strip()


def check_database():
	try:
		print('check_database')
		c = conn.cursor()
		#c.execute('''SELECT * FROM wiktionary''')
		c.execute('''SELECT count(title) FROM wiktionary''')
		result = c.fetchall()
		#print("titles", result)
		return result and len(result) > 0 and result[0][0] > 1
	except sqlite3.OperationalError:
		return 0


def download(url, filename):
	try:
		from urllib2 import urlopen
		from urllib import urlretrieve, urlencode
	except ImportError:
		from urllib.request import urlopen, urlretrieve  # py3 HELL
		from urllib.parse import urlencode
	print("Downloading ", url, "to", filename)
	urlretrieve(url, filename)


def preprocess(report=True):
	if check_database():
		if report:
			print("local sqlite already built")
		return
	else:
		print("building local sqlite database")
	prepare_database()
	parser = xml.sax.make_parser()
	parser.setContentHandler(StreamHandler())
	try:
		filename = 'enwiktionary-latest-pages-articles.xml.bz2'
		if not exists(filename):
			download(url, filename)
		f = bz2.open(filename, mode='rt', encoding='utf8')
		print("parsing xml")
		parser.parse(f)
	except StopIteration:
		print('enwiktionary ')
	finally:
		conn.commit()  #remaining inserts


def all(word, rows='content', fuzzy=False, limit=1000):
	preprocess(False)
	c = conn.cursor()
	sql = "SELECT %s FROM wiktionary %s limit %d"
	if fuzzy:
		criterion = "where title like '%" + word + "%'"
	else:
		criterion = "where title = '%s'" % word
	if limit == -1 or word=='*':
		criterion = ''
	print(sql % (rows, criterion, limit))
	c.execute(sql % (rows, criterion, limit))
	results = c.fetchall()
	return [r[0] for r in results]


def query(word):
	return all(word, fuzzy=False, limit=1)


def fuzzy(word):
	return all(word, fuzzy=True)


def titles(word):
	return all(word, rows='title', fuzzy=True)

def count_titles(word='*'):
	return all(word, rows='count(*)', fuzzy=True)

def dump_titles():
	xs = all('*', rows='title', limit=100)
	print(xs)


if __name__ == '__main__':
	preprocess()
	#prepare_database()
	w=search('דֶּלֶת')
	print(w)
	dump_titles()
	nr=count_titles()
	print( nr)
	w = titles('ⲗⲁ')
	print(w)
	w = query('𐎄𐎍𐎚')  # porta door spalt
	print(w)
	

