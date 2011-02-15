import datetime
from django.template.defaultfilters import slugify
from django.core.validators import validate_slug, MinValueValidator, MaxValueValidator

from django.db import models
from django.db.models import Model

now = datetime.datetime.now

def diff(a,b):
	return ""
	
def set_mug_path(instance=None, **kwargs):
	d = instance.orig_date.date()
	path = "mugs/%s/%s/%s-%s" % d.year, d.month, d.day, slugify(instance.title)
	return path
	

class BasePost(Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(validators=[validate_slug])
	_text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now, editable=False)
	orig_date = models.DateTimeField('date published', default=now, editable=False)
	previous = models.OneToOneField('self', null=True, editable=False)
	rating = models.SmallIntegerField(editable=False, validators=[MinValueValidator(0), MaxValueValidator(10)])
		
	def __unicode__(self):
		return self.title + " - " + str(self.pub_date.ctime())


class Post(BasePost):
	mug = models.ImageField(upload_to=set_mug_path)
	
	to_be_updated = []
		
	def get_text(self):
		return self._text
	def set_text(self, text):
		diffed_post = BasePost( title = self.title,
			slug = self.slug,
			_text = diff( self._text , text),
			pub_date = self.pub_date,
			orig_date = self.orig_date,
			previous = self.previous,
			rating = self.rating )
			
		self.to_be_updated.append(diffed_post)
		self.previous = diffed_post
		self._text = text
		self.pub_date = now()
	
	text = property(get_text, set_text)
	
	def save(self, *args, **kwargs):
		for post_diff in self.to_be_updated:
			post_diff.save()
		self.to_be_updated = []
		PostBase.save(self, *args, **kwargs)
	
	def __unicode__(self):
		return self.title
	
