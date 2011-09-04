import re
from functools import partial

from unidecode import unidecode

from django.shortcuts import redirect
from django.views.defaults import page_not_found
from django.db.models.signals import post_save

from views import UnknownMonth, months
from models import Post, Tag, known_words, all_words

word_set = all_words()

class SpellingRedirectMiddleware(object):
	def __init__(self):
		self.correct_month = partial(correct, lambda m: m in months)

		self.known = lambda w: w in word_set
		def select_word(words):
			words = known_words(words)
			return max(words, key=lambda w: w.num).word
		
		self.correct_word = partial(correct, self.known, select=select_word)
		
		
	def process_exception(self, request, exception):
		if isinstance(exception, UnknownMonth):
			new_month = self.correct_month(exception.month)
			if new_month in months:
				print new_month
				path = re.sub(re.compile(r'(\d{4}/)\w{3,9}(/)', re.UNICODE), "\g<1>"+new_month+"\g<2>", request.path, 0)
				print path
				return redirect(path, permanent=True)
			return page_not_found(request)
			
		elif isinstance(exception, Post.DoesNotExist):
			slug = re.search(r'(blog|admin)/(\d{4}/(\d{1,2}|\w{3,9})/\d{1,2}/)?(\w+[\w-]+\w+)/', request.path, re.UNICODE).group(4)
			new_slug = self._fix_words(slug.split("-"), request)
			if new_slug is None:
				return page_not_found(request)
			new_slug = "-".join(new_slug)
			if new_slug != slug:
				path = re.sub(re.compile(r'(blog|admin)/(\d{4}/(\d{1,2}|\w{3,9})/\d{1,2}/)?\w+[\w-]+\w+(/)', re.UNICODE), "\g<1>/"+new_slug+"\g<4>", request.path, 0)
				return redirect(path, permanent=True)
			return page_not_found(request)
		
		elif isinstance(exception, Tag.DoesNotExist):
			match = re.search(r'tag/(\w[\w\+]+\w)/', request.path, re.UNICODE)
			if match:
				separator = "_"
			else:
				match = re.search(r'tag/(\w[\w\+\.]+\w)/', request.path, re.UNICODE)
				if not match: return page_not_found(request)
				separator = "\."
			tags = match.group(1)
			tag_list = [re.sub(separator, " ", tag) for tag in tags.split("+")]
			separator = "." if separator == "\." else separator
			new_tags=[]
			for tag in tag_list:
				new_tag = self._fix_words(tag.split(), request)
				if new_tag is None:
					return page_not_found(request)
				new_tags.append(separator.join(new_tag))
			new_tags = "+".join(new_tags)
			if new_tags != tags:
				path = re.sub(re.compile(r'(tag/)\w[\w\+\.]+\w(/)', re.UNICODE), "\g<1>"+new_tags+"\g<2>", request.path, 0)
				return redirect(path, permanent=True)
			return page_not_found(request)


	def _fix_words(self, words, request):
		new_words = []
		for word in words:
			word = unidecode(word)
			if not self.known(word):
				word = self.correct_word(word)
				if not self.known(word):
					return None
			new_words.append(word)
		return new_words



def update_known_words(sender, **kwargs):
	global word_set
	word_set = all_words()

post_save.connect(update_known_words, sender=Post, dispatch_uid="new_post", weak=False)
post_save.connect(update_known_words, sender=Tag, dispatch_uid="new_tag", weak=False)



# Here's the algorithm used by this middleware for the spellchecking
# It's taken from this Peter Norvig's page: http://norvig.com/spell-correct.html
# I like it because it's very simple, and since this redirector doesn't need to know all the
# english words (and in fact it would be counter-productive if it would) I thought it would be nice
# to use it with only the words already know by the application because stored in the db
# (and thus we don't need to have a separate on-disk index for this functionality)

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
	splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
	deletes = [a + b[1:] for a, b in splits if b]
	transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
	replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
	inserts = [a + c + b for a, b in splits for c in alphabet]
	return set(deletes + transposes + replaces + inserts)

def known_edits2(word, known):
	return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if known(e2))

def correct(known_func, word, select=max):
	candidates = filter(known_func, edits1(word)) or known_edits2(word, known_func) or [word]
	return select(candidates)
	# pay attention: it may return a list
