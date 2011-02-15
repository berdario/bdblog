import datetime

from django.db import models
from django.db.models import Model

now = datetime.datetime.now

def diff(a,b):
	return ""

class Post(Model):
	title = models.CharField(max_length=200)
	_text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now)
	orig_date = models.DateTimeField('date published', default=now)
	to_be_updated = []
	
	
	def get_text(self):
		return self._text
	def set_text(self, text):
		self.to_be_updated.append( PostDiff( title = self.title,
			text = diff( self._text , value),
			pub_date = self.pub_date,
			orig_date = self.orig_date ))
		self._text = text
		self.pub_date = now()
	
	text = property(get_text, set_text)
	
	def save(self, *args, **kwargs):
		for post_diff in self.to_be_updated:
			post_diff.save()
		self.to_be_updated = []
		Model.save(self, *args, **kwargs)
	
	def __unicode__(self):
		return self.title

class PostDiff(Post):
	original = models.OneToOneField(Post, null=True)
	
	def __unicode__(self):
		return self.title + " - " + str(self.pub_date.ctime())
	
