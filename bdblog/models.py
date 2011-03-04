import datetime
from unidecode import unidecode
from unicodedata import normalize
import re
from django.template.defaultfilters import stringfilter
from django.core.validators import validate_slug, RegexValidator, MinValueValidator, MaxValueValidator

from django.db import models
from django.db.models import Model, F, Q

now = datetime.datetime.now

def diff(a,b):
	return ""
	
def set_mug_path(instance=None, **kwargs):
	d = instance.orig_date
	path = "mugs/%s/%s/%s-%s" % d.year, d.month, d.day, instance.slug
	return path
	
	
class Tag(Model):
	_tag = models.CharField(max_length=200)
	ascii_tag = models.CharField(max_length=500, validators=[RegexValidator('^[a-z ]*$')])
	
	@property
	def tag(self):
		return self._tag
		
	@tag.setter
	def tag(self, value):
		self._tag = value
		self.ascii_tag = unidecode(value)
	
	def __init__(self, *args, **kwargs):
		Model.__init__(self, *args, **kwargs)
		self.ascii_tag = unidecode(self._tag) #get_or_create is called with _tag, and thus won't trigger the tag setter
		for word in self.ascii_tag.split():
			if not known(word):
				Word(word).save()
	
	def __unicode__(self):
		return self.tag


class BasePost(Model):
	_title = models.CharField(max_length=200)
	_text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now, editable=False)
	orig_date = models.DateField('date published', auto_now_add=True)
	orig_time = models.TimeField('time published', auto_now_add=True)
	previous = models.OneToOneField('self', null=True, editable=False)
	rating = models.SmallIntegerField(default=0, editable=False, validators=[MinValueValidator(0), MaxValueValidator(10)])
		
	def __unicode__(self):
		return self._title + " - " + str(self.pub_date.ctime())
		
	class Meta(object):
		ordering = ['orig_date', 'orig_time']


class Post(BasePost):
	slug = models.SlugField(validators=[validate_slug])
	mug = models.ImageField(upload_to=set_mug_path)
	_tags = models.ManyToManyField(Tag)
	
	def __init__(self, *args, **kwargs):
		self.to_be_updated = []
		BasePost.__init__(self, *args, **kwargs)
		
	@property
	def text(self):
		return self._text
	
	@text.setter
	def text(self, text):
		if self._text:
			diffed_post = BasePost( _title = self.title,
				_text = diff( self._text , text),
				pub_date = self.pub_date,
				orig_date = self.orig_date,
				orig_time = self.orig_time,
				previous = self.previous,
				rating = self.rating )
			
			self.to_be_updated.append(diffed_post)
			self.previous = diffed_post
			
		self._text = text
		self.pub_date = now()
	
	@property
	def title(self):
		return self._title
	
	@title.setter
	def title(self, title):
		self._update_title_words(-1)
		self._title = title
		self.slug = slugify(unidecode(title))
		self._update_title_words()
		# some words may be updated 2 times: once with -1 and once with 1
		# can't use a set instead of list by using F(): the old change would be forgotten
		# checking if new words are in the old title, and avoid to update them altogheter 
		# would add more complexity than it's worth it
			
	@property
	def tags(self):
		return self._tags
		
	@tags.setter
	def tags(self, tag_names):
		tag_list = [Tag.objects.get_or_create(_tag=name)[0] for name in tag_names]
		self._tags = tag_list
	
	
	def _update_title_words(self, delta=1):
		if self.slug:
			for word in self.slug.split("-"):
				occurrence = Word.objects.get_or_create(word=word)[0]
				occurrence._num = F('_num') + delta
				self.to_be_updated.append(occurrence)
	
	def delete(self, *args, **kwargs):
		self._update_title_words(-1)
		self.save()
		BasePost.delete(self, *args, **kwargs)
	
	def save(self, *args, **kwargs):
		for other_model in self.to_be_updated:
			other_model.save()
		self.to_be_updated = []
		self.previous = self.previous
		# ugly hack: otherwise, since the previous hasn't been saved yet, it might not have a pk
		# and thus the relationship would not be valid 
		# (but in other cases django complains with a ValueError, don't know why it doesn't do it here)
		BasePost.save(self, *args, **kwargs)
	
	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return "/blog/%s/%s/%s/%s" % (
			self.orig_date.year,
			self.orig_date.month,
			self.orig_date.day,
			slugify(self.title)
			)
		# the permalink decorator will resolve with admin=True, is unable to resolve with the "unicode slug"
		# and is also unable to resolve the optional date: thus I'm writing the url explicitly

class Word(Model):
	word = models.CharField(primary_key=True, unique=True, db_index=True, max_length=30, validators=[RegexValidator('^[a-z]*$')])
	_num = models.IntegerField(default=0, editable=False)
			
	@property
	def num(self):
		count = 0
		for tag in Tag.objects.filter(ascii_tag__contains=self.word):
			count += tag.post_set.count()
		return self._num + count
	
	def __unicode__(self):
		return self.word
	
@stringfilter
def slugify(value):
	value = normalize('NFKD', value)
	value = re.sub(re.compile('[?,:!@#~`+=$%^&\\*()\[\]{}<>"]', re.UNICODE), '', value, 0).strip().lower()
	# sub('[^\w\s-]', '', value) like in the default slugify won't work since it'll catch also unicode letters
	# TODO, check this again: it seems that I wasn't really supplying re.UNICODE to the substitution
	return re.sub(re.compile('[-\s]+', re.UNICODE), '-', value, 0)

def known(word):
	return Word.objects.filter(pk=word).exists()
	
def all_words():
	return set(w.word for w in Word.objects.all())

def word_score(word):
	if not known(word): return 0
	return Word.objects.filter(pk=word)[0].num
		
def get_post(slug, date=None):
	slug = unidecode(slug)
	q = Post.objects
	if date:
		q = q.filter(orig_date=date)
	return q.get(slug=slug)

	
def get_posts(year, month=None, day=None, page=1, page_range=20):
	start, end = (page-1)*page_range, page*page_range
	q = Post.objects.filter(orig_date__year=year)
	if month:
		q = q.filter(orig_date__month=month)
		if day:
			q = q.filter(orig_date__day=day)
	return q[start:end]


def from_tags(tags, page=1, page_range=20):
	start, end = (page-1)*page_range, page*page_range
	q = Post.objects
	for t in tags:
		tag = Tag.objects.get(Q(_tag=t) | Q(ascii_tag=t))
		q = q.filter(_tags=tag)
	return q[start:end]
	
