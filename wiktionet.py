#!/usr/bin/env python3
#ln /me/dev/python/extensions.py
#from extensions import *
import re
#from wiktionary.wiktionaryimporter import query, search, titles
try:
  from wiktionaryimporter import query, search, titles
except:
	from .wiktionaryimporter import query, search, titles
	
cache={}
debug_wiktionary= False
def word( title):
		if title in cache:
		 	 return cache[ title]
		return Word( title)
		 	  

def flatten(l):
	if isinstance(l, (list, tuple)):
		for k in l:
			if isinstance(k, (list, tuple)):
				l.remove(k)
				for j in k:
					l+=flatten(j)
			# else keep
		return l
	else:
		return [l]
	# verbose("NOT flattenable: %s"%s)


def clean(link):
	if isinstance(link , tuple): return link
	if isinstance(link , list): return flatten(list(map(clean,link)))
	links=link.split("|")
	return flatten(list(filter(lambda l:not '=' in l,links)))
	# return xlist links.select(lambda l:not '=' in l)



class Word():
	def __init__(self, title, content=''):
		if not content:
			results = query(title)
			if not results and not ':' in title : results = query(title. capitalize())
			if not results and not ':' in title : results = query(title. lower())
			if debug_wiktionary: print(results)
			if results:
				content = results[0]
		self.content = content
		self.text = self.content.strip()+"===="
		self. title= title
		cache[ title]= self
		if len(content)<100 and len(self.links())==1 :
				redir=self.links()[0]
				print("redirect to "+redir)
				# self=Word(redir)
				self.content = str(query(redir))
				self.text = self.content#.strip()+"===="

	def parents(self):
		return re.findall(r'\{inh\|(.*?)\|(.*?)\|([^\}]*)', self.text)
	
	def hyponyms(self):
		try:
			 if not self. text: return
			 text= re. findall( r'Hyponyms==+(.*?)==',self.text)[0]
			 return re.findall(r'\{ws\|(.*?)\}', text)
		except : 
			return word('Thesaurus:'+self.title).hyponyms() if not ':' in self.title else []

	def antonyms(self):
		xs= re.findall(r'\{ant\|(.*?)\}', self.text)
		if xs: return
		try:
			 if not self. text: return
			 text= re. findall( 'Antonyms==+(.*?)==',self.text)[0]
			 return re.findall(r'\{ws\|(.*?)\}', text)
		except : 
			return word('Thesaurus:'+self.title).Antonyms() if not ':' in self.title else []
		

	def Hypernyms(self):
		try:
			 if not self. text: return
			 text= re. findall( r'Hypernyms==+(.*?)==',self.text)[0]
			 return re.findall(r'\{ws\|(.*?)\}', text)
		except : 
			return word('Thesaurus:'+self.title).Hypernyms() if not ':' in self.title else []
	

	def compounds(self):
		# compounds = re.findall(r'\{compound\|(.*?)\|(.*?)\|(.*?)\}', self.text)
		compounds=re.findall(r'\{Han char.*?ids=(.*?)\}',self.text)
		if not compounds:
			compounds = clean(re.findall(r'\{Han compound\|(.*?)\}',self.text))
		return flatten(compounds)
	

	def etymology(self):
		try:
			text= re. findall( r'Etymology==+(.*?)==',self.text)[0]
		except : text=self.text # self. content ?
		found = re.findall(r'\{inh\|(.*?)\|([^\}]*)', self.text)
		# found = re.findall(r'\{inh\|(.*?)\|(.*?)\|([^\}]*)', text)
		found += re.findall(r'-forms\|alt=(.*?)\|',text)
		found += re.findall(r'\{der\|(.*?)\|(.*?)\|([^\}]*)',text)
		found += re.findall(r'\{m\|(.*?)\|(.*?)[\||\}]', text) # meronym?
		found += re.findall(r'\{suffix\|([^\}]*)', text)
		found += re.findall(r'\{plural of\|([^\}]*)', self.text)
		found += re.findall(r'\{bor\|(.*?)\|(.*?)\|([^\}]*)', self.text) #borrowing
		found += self.compounds()
		return clean(found)

	def derived(self):
		found = re.findall(r'\{der\|(.*?)\|(.*?)\|([^\}]*)', self.text)
		found += re.findall(r'\{m\|(.*?)\|([^\}]*)', self.text) # meronym?
		found += re.findall(r'\{l\|(.*?)\|([^\}]*)', self.text)
		found += re.findall(r'\{der4\|([^\}]*)', self.text)
		try:
			text= re. findall( r'Derived characters==+(.*?)==',self.text)[0]
			found += re.findall(r'\{l\|(.*?)\|([^\}]*)', text) # done above!
			found += re.findall(r'\[\[(.*?)\]\]',text)
		except : pass
		return found

	def context(self):
		found= re.findall(r'\{lb\|(.*?)\|([^\}]*)', self.text)
		found += re.findall(r'\{sense\|(.*?)\}', self.text)
		return found
		
	def rhymes(self):
		return re.findall(r'\{rhymes\|(.*?)\}', self.text)
		
	def examples(self):
		return re.findall(r'\{ux\|(.*?)\}', self.text)

	def anagrams(self):
		return re.findall(r'\{anagrams\|(.*?)\}', self.text)

	def references(self):
		return re.findall(r'\{R:(.*?)\}', self.text)

	def qualifiers(self):
		found = re.findall(r'\{qualifier\|(.*?)\}', self.text)
		found += re.findall(r'\{rfd\|(.*?)\}', self.text)
		return found

	def parts(self):
		found = re.findall(r'\{suffix\|(.*?)\}', self.text)
		found += re.findall(r'\{hyph\|(.*?)\}', self.text)
		found += re.findall(r'\{hyphenation\|(.*?)\}', self.text)
		return found
		
	def links(self):
		links = re.findall(r'\{also\|(.*?)\}', self.text)
		links += re.findall(r'-see\|(.*?)\}', self.text)
		links += re.findall(r'\{w\|(.*?)\}', self.text)
		#links += re.findall(r'\{l\|(.*?)\}', self.text)
		links += re.findall(r'\[\[(.*?)[\||\]]', self.text)
		return links
		
	def Thesaurus(self):
		 if not self. text: return
		 found = re.findall(r'\[(Thesaurus:.*?)\]', self.text)
		 if not found :return self. synonyms()
		 return Word( found[ 0]). synonyms()

	def synonyms(self):
		links = re.findall(r'\{also\|(.*?)\}', self.text)
		links += re.findall(r'\{ws\|(.*?)\}', self.text)
		links += re.findall(r'\{syn\|(.*?)\}', self.text)
		links += re.findall(r'\{l\|(.*?)\}', self.text)
		links += re.findall(r'\{w\|(.*?)\}', self.text)
		return links

	def declensions(self):
		found = re.findall(r'\{(\w+)-noun\|(.*?)\}', self.text)
		#found += re.findall(r'\{.*?\-verb|(.*?)\|([^\}]*)', self.text)
		return found

	def pronounciations(self):
		ipas = re.findall(r'\{IPA\|([^\}]*)', self.text)
		ipas += re.findall(r'\{enPR\|([^\}]*)', self.text)
		ipas += re.findall(r'pron\|m=(.*?)\|',self.text)
		#ipas += re.findall(r'\{\w+\-IPA\|(.*?)\|([^\}]*)', self.text)
		return ipas

	def translations(self):
		translations = re.findall(r'\{t\+\|(.*?)\|([^\}]*)', self.text)
		translations += re.findall(r'\{t\|(.*?)\|([^\}]*)', self.text)
		translations += re.findall(r'\{t\+check\|(.*?)\|([^\}]*)', self.text)
		translations += re.findall(r'\{t\-simple\|(.*?)\|([^\}]*)', self.text)
		try:
			text= re. findall( r'Definitions==+(.*?)==',self.text)[0]
			translations += re.findall(r'\[\[(.*?)\]', text)
		except : pass		
		try:
			text= re. findall( r'Noun==+(.*?)==',self.text)[0]
			translations += re.findall(r'\[\[(.*?)\]', text)
		except : pass
		try:
			text= re. findall( r'Verb==+(.*?)==',self.text)[0]
			translations += re.findall(r'\[\[(.*?)\]', text)
		except : pass
		return translations

	def describe(self):
		if not self. title:
			return
		if not self. text:
			return
		from pprint import pprint as prettyprint
		import pprint 
		prettyprint=pprint.PrettyPrinter(indent=2).pprint #wtf api
		print( self. json())
		prettyprint( self. json())
		return self.json()
		word= self
		print('parts',word. parts())
		print('parents',word.parents())
		
		print('links',word.links())
		print('anagrams',word.anagrams())
		print('context',word.context())
		print('rhymes',word. rhymes())
		print('references',word.references())
		print('pronounciations',word.pronounciations())
		print('derived',word.derived())
		print('qualifiers',word.qualifiers())
		print('etymology',word.etymology())
		print('declensions',word.declensions())
		print('examples', word.examples())
		print('synonyms', word.synonyms())
		
		print('hyponyms', word.hyponyms())
		print('antonyms', word.hyponyms())
		print('Hypernyms', word.hyponyms())
		print('Thesaurus', word.Thesaurus())
		print('translations',word.translations())
		# print('content',word.content)
		return self.json()

	def json(word):
		return {
		# 'content':word.content, #raw
			'parts':word. parts(),
			'parents':word.parents(),
			'links':word.links(),
			'anagrams':word.anagrams(),
			'context':word.context(),
			'rhymes':word. rhymes(),
			'references':word.references(),
			'pronounciations':word.pronounciations(),
			'derived':word.derived(),#derivatives
			'qualifiers':word.qualifiers(),
			'etymology':word.etymology(),
			'compounds':word.compounds(),
			'declensions':word.declensions(),
			'examples': word.examples(),
			'synonyms': word.synonyms(),
			'hyponyms': word.hyponyms(),
			'antonyms': word.hyponyms(),
			'Hypernyms': word.hyponyms(),
			'Thesaurus': word.Thesaurus(),
			'translations':word.translations()
		}
		
def describe(word):
	 if isinstance(word,str ):
	  word=Word(word)
	 word. describe()
	 

#word = Word('Thesaurus:copulate')
#word = Word('Thesaurus:write')
if __name__ == '__main__':
	from pprint import pprint
	import sys
	if len(sys.argv)>1:
		arg=sys.argv[1] 
	else:
		 	debug_wiktionary= True
		 	arg='sex' # 'Pannous' Quasiris
	describe(arg)
	#print(search('head|akk'))







"""
t|yue|字典|tr=zi6 din2|sc=Hani
t|ckt|вэтгавкаԓекаԓ|tr=vėtgavkaḷekaḷ
ux Exempel
ant Antonym
syn synonym
anagrams|en|Boko|Koob|boko|bòkò|kobo
wikipedia|dab=free
desc|tpi|bok 	descendant
desc|ny|buku|bor=1  descendant borrowing?
bor|en|la|gratis 	borrowing
der|en|gem-pro|*bakaną|t=to bake 	derivative
inh|en|enm|booken
m|ang|frēoġan||to free; make free  from/meronym?
m|sa|बभ्रु||tr=babhrú|reddish-brown
PIE root|en|gʷerH
cog|no|fri||free 	cognate
gloss|to become
IPA|/fɹiː/|lang=en
also|-free
alternative form of|booke|lang=enm
R:Etymonline reference?
w Wikipedia
rhymes|iː|lang=en
audio|En-uk-free.ogg|Audio (UK)|lang=en
quote-book|year=1866|author=William Henry Ward|title=
head|lb|verb form
head|pdc|adjective
lb language barrier?  social/obsolete/computing/transitive
qualifier|dated/informal/obsolete/character dictionary ?
rfd|obsolete, useless
rel-top|Sciences
homophones|pi|π|lang=en
defdate|from 15th c.
n-g|changed after 1956 to
en-verb|dictionar|ies ...
ro-adv
ro-adj|inv
ro-decl-adj|inv
Latn-def|co|letter|1|a
l|de|Wörterbuch link/like?
compound|cop|ⲱϣ|ⲗⲏⲗ
; phonetic values:
	\n ....
"""

