import datetime

from django.db import models
from django.db.models import Model

now = datetime.datetime.now

class Post(Model):
	title = models.CharField(max_length=200)
	text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now)
	orig_date = models.DateTimeField('date published', default=now)
	
	def __unicode__(self):
		return self.title

class PostDiff(Post):
	original = models.OneToOneField(Post, null=True)
	
	def __unicode__(self):
		return self.title + " - " + str(self.pub_date.ctime())
	
