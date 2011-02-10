import datetime

from django.db import models
from django.db.models import Model

now = datetime.datetime.now

def diff(a,b):
	return ""

class Post(Model):
	title = models.CharField(max_length=200)
	#Model.__setattr__(self, "text", models.TextField() )
	pub_date = models.DateTimeField('last change', default=now)
	orig_date = models.DateTimeField('date published', default=now)
	to_be_updated = []
	#text = models.TextField()
	
	#def __init__(self, *args, **kwargs):
	#	Model.__setattr__(self, "text", models.TextField() )
	#	Model.__init__(self, *args, **kwargs)
	
	def __new__(cls, *args, **kwargs):
		print "eccoci"
		obj = Model.__new__(cls, *args, **kwargs)
		Model.__setattr__(obj, "text", models.TextField() )
		return obj
		
	
	def __setattr__(self, name, value):
		if (name == "text"):
			self.to_be_updated.append( PostDiff( title = self.title,
				text = diff( Model.__getattribute__(self,"text") , value),
				pub_date = self.pub_date,
				orig_date = self.orig_date ))
			Model.__setattr__(self, name, value)
			self.pub_date = now()
		else:
			Model.__setattr__(self, name, value)
	
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
	
