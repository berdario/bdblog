import datetime
from unidecode import unidecode
from django.template.defaultfilters import slugify
from django.core.validators import validate_slug, RegexValidator, MinValueValidator, MaxValueValidator

from django.db import models
from django.db.models import Model, F

now = datetime.datetime.now

def diff(a,b):
	return ""
	
def set_mug_path(instance=None, **kwargs):
	d = instance.orig_date.date()
	path = "mugs/%s/%s/%s-%s" % d.year, d.month, d.day, instance.slug
	return path
	
	
class Tag(Model):
	tag = models.CharField(max_length=200, validators=[RegexValidator('^[a-z ]*$')])
	
	def __init__(self, *args, **kwargs):
		Model.__init__(self, *args, **kwargs)
		for word in self.tag.split():
			if not known(word):
				Word(word).save()
	
	def __unicode__(self):
		return self.tag


class BasePost(Model):
	_title = models.CharField(max_length=200)
	_text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now, editable=False)
	orig_date = models.DateTimeField('date published', default=now, editable=False)
	previous = models.OneToOneField('self', null=True, editable=False)
	rating = models.SmallIntegerField(default=0, editable=False, validators=[MinValueValidator(0), MaxValueValidator(10)])
		
	def __unicode__(self):
		return self._title + " - " + str(self.pub_date.ctime())


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
		diffed_post = BasePost( _title = self.title,
			_text = diff( self._text , text),
			pub_date = self.pub_date,
			orig_date = self.orig_date,
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
		#self._tags.clear()
		tag_list = [Tag.objects.get_or_create(tag=name)[0] for name in tag_names]
		self._tags = tag_list
	
	
	def _update_title_words(self, delta=1):
		if self.slug:
			for word in self.slug.split("-"):
				occurrence = Word.objects.get_or_create(word=word)[0]
				occurrence._num = F('_num') + delta
				self.to_be_updated.append(occurrence)
	
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

class Word(Model):
	word = models.CharField(primary_key=True, max_length=30, validators=[RegexValidator('^[a-z]*$')])
	_num = models.IntegerField(default=0, editable=False)
			
	@property
	def num(self):
		count = 0
		for tag in Tag.objects.filter(tag__contains=self.word):
			count += tag.post_set.count()
		return self._num + count
	
	def __unicode__(self):
		return self.word
	

def known(word):
	return bool(Word.objects.filter(pk=word)[:1])
