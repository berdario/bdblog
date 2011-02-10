import datetime

from django.db import models
from django.db.models import Model

now = datetime.datetime.now

class Post(Model):
	title = models.CharField(max_length=200)
	text = models.TextField()
	pub_date = models.DateTimeField('last change')
	orig_date = models.DateTimeField('date published')
	
	def __init__(self, title="", text="", orig_date=None, pub_date=None, *args, **kwargs ):
		if not pub_date:
			pub_date = now()
		if not orig_date:
			orig_date = pub_date
		Model.__init__(self, title=title, text=text, orig_date=orig_date, pub_date=pub_date, *args, **kwargs )
	
	def __unicode__(self):
		return self.title

class PostDiff(Post):
	original = models.OneToOneField(Post, null=True)
	
	def __init__(self, original, text, *args, **kwargs ):
		title, pub_date, orig_date = original.title, original.pub_date, original.orig_date
		if pub_date == orig_date:
			original = None
		Post.__init__(self, title, text, orig_date=orig_date, pub_date=pub_date, original=original, *args, **kwargs )
	
	def __unicode__(self):
		return self.title + " - " + str(self.pub_date.ctime())
	
