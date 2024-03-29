import os
import datetime
from collections import defaultdict
from unidecode import unidecode
from unicodedata import normalize
import re
from django.template.defaultfilters import stringfilter
from django.core.validators import validate_slug, RegexValidator, MinValueValidator, MaxValueValidator
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import IntegerField, CharField, HiddenInput, ModelForm, ValidationError
from django.forms.models import modelformset_factory

try:
	from django.utils.timezone import now
except ImportError:
	from datetime import datetime
	from settings import TIME_ZONE
	from pytz import timezone
	from functools import partial
	now = partial(datetime.now, timezone(TIME_ZONE))

from django.db import models
from django.db.models import Model, F, Q

from PIL import Image
from differ import diff

def set_mug_path(instance, filename):
	d = instance.orig_date
	ext = filename.split(".")[-1]
	dest_file = "%s-%s-%s.%s" % (d.day, d.month, instance.slug, ext)
	path = os.path.join("mugs", str(d.year), dest_file)
	return path
	
	
class Tag(Model):
	tag = models.CharField(max_length=200)
	ascii_tag = models.CharField(max_length=500, validators=[RegexValidator('^[a-z ]*$')])
	
	def save(self, *args, **kwargs):
		self.ascii_tag = unidecode(self.tag)
		words = self.ascii_tag.split()
		known_words_list = known_words(words)
		for word in words:
			new_word = Word(word)
			if not new_word in known_words_list:
				new_word.save()
		Model.save(self, *args, **kwargs)
	
	def __unicode__(self):
		return self.tag


class BasePost(Model):
	title = models.CharField(max_length=200)
	_text = models.TextField()
	pub_date = models.DateTimeField('last change', default=now, editable=False)
	orig_date = models.DateField('date published', auto_now_add=True)
	orig_time = models.TimeField('time published', auto_now_add=True)
	previous = models.OneToOneField('self', null=True, editable=False)
	rating = models.SmallIntegerField(default=0, editable=False, validators=[MinValueValidator(0), MaxValueValidator(10)])
		
	def __unicode__(self):
		return self.title + " - " + str(self.pub_date.ctime())
		
	class Meta(object):
		ordering = ['-orig_date', '-orig_time']


class Post(BasePost):
	text = models.TextField()
	slug = models.SlugField(validators=[validate_slug])
	mug = models.ImageField(upload_to=set_mug_path)
	_tags = models.ManyToManyField(Tag)
	tags = models.CharField(max_length=200)
	_temp_previous = None
	
	def _handle_text_change(self, text):
		if self._text and text != self._text:
			diffed_post = BasePost( title = self.title,
				_text = diff( self._text , text),
				pub_date = self.pub_date,
				orig_date = self.orig_date,
				orig_time = self.orig_time,
				previous = self.previous,
				rating = self.rating )
						
			self.previous = None
			self._temp_previous = diffed_post
			# making previous None, to avoid key collision in the 1:1 rel
			# after calling the super().save(), it's safe to save the diffed_post and bind it to self.previous
		
		self._text = text
		self.pub_date = now()
	
	
	def _handle_title_change(self):
		new_slug = slugify(unidecode(self.title))
		if not self.slug or self.slug != new_slug:
			self.changed_words = defaultdict(lambda : 0)
			self._update_title_words(-1)
			self.slug = new_slug
			self._update_title_words()
			
			changes = defaultdict(list)
			for k,v in self.changed_words.iteritems():
				changes[v].append(k)
			for delta, words in changes.iteritems():
				if delta != 0:
					known_words(words).update(_num=F('_num') + delta)
			self.changed_words.clear()
	
	def _update_title_words(self, delta=1):
		if self.slug:
			tokens = self.slug.split("-")
			previous_words = [w.word for w in known_words(tokens)]
			new_words = [Word(word) for word in tokens if word not in previous_words]
			for word in new_words:
				word.save()
			for word in tokens:
				self.changed_words[word]+=delta
	
	def delete(self, *args, **kwargs):
		self.title = ""
		self._handle_title_change()
		self.save()
		BasePost.delete(self, *args, **kwargs)
	
	def save(self, *args, **kwargs):
		resave = self.pk is None
		if not resave:
			# the very first time, you can't create a m2m relationship 
			self._tags = [Tag.objects.get_or_create(tag=name)[0] for name in self.tags.split("+")]
		self._handle_text_change(self.text)
		self._handle_title_change()
		BasePost.save(self, *args, **kwargs)
		if self._temp_previous:
			self.previous = self._temp_previous
			self.previous.save()
			self.previous = self.previous
			# ugly hack: otherwise, since the previous hasn't been s
			# and thus the relationship would not be valid 
			# (but in other cases django complains with a ValueError
			self._temp_previous = None
			resave = True
		if resave:
			self.save(*args, **kwargs)
			
	
	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return u"/blog/%s/%s/%s/%s" % (
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
	value = normalize('NFKC', value)
	value = re.sub(re.compile('[?,:!@#~`+=$%^&\\*()\[\]{}<>"]', re.UNICODE), '', value, 0).strip().lower()
	# sub('[^\w\s-]', '', value) like in the default slugify won't work since it'll catch also unicode letters
	# TODO, check this again: it seems that I wasn't really supplying re.UNICODE to the substitution
	return re.sub(re.compile('[-\s]+', re.UNICODE), '-', value, 0)


def known_words(words):
	query = Q()
	for word in words:
		query |= Q(pk=word)
	return Word.objects.filter(query)

def all_words():
	return set(Word.objects.values_list('word', flat=True))

class PostForm(ModelForm):
	x = IntegerField(min_value=1, widget=HiddenInput(), required=False)
	y = IntegerField(min_value=1, widget=HiddenInput(), required=False)
	size = IntegerField(min_value=1, widget=HiddenInput(), required=False)
	canvasData = CharField(widget=HiddenInput(), required=False)

	class Meta:
		model = Post
		fields = ('title', 'text', 'mug', 'tags')

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.fields['mug'].required = False

	def clean(self):
		if not self.cleaned_data['mug']:
			data = self.cleaned_data['canvasData']
			if data:
				datatype = data.split(";")[0].split("data:")[-1]
				data = data.split("base64,",1)[-1]
				name = "canvas." + datatype.split("/")[-1]
				self.instance.mug = SimpleUploadedFile(name, data.decode("base64"), content_type=datatype)
			else:
				raise ValidationError("You have to supply an image")
		return self.cleaned_data

	def save(self, *args, **kwargs):
		mug, x, y, size = [self.cleaned_data[key] for key in ('mug', 'x', 'y', 'size')]
		mug = mug or self.instance.mug
		if get_image_dimensions(mug) != (100,100):
			if all([x, y, size]):
				make_thumb(mug, (x, y), size)
		return super(PostForm, self).save(*args, **kwargs)

PostFormSet = modelformset_factory(Post, form=PostForm)

def make_thumb(mug, coord, size):
	image = Image.open(mug.path)
	image = image.crop((coord[0], coord[1], coord[0] + size, coord[1] + size))
	image.thumbnail((100, 100), Image.ANTIALIAS)
	image.save(mug.path)

def get_post(slug, date=None):
	slug = unidecode(slug)
	q = Post.objects
	if date:
		q = q.filter(orig_date=date)
	return q.get(slug=slug)

	
def get_posts(year=None, month=None, day=None, page=1, page_range=20):
	start, end = (page-1)*page_range, page*page_range
	q = Post.objects.all()
	if year:
		q = q.filter(orig_date__year=year)
		if month:
			q = q.filter(orig_date__month=month)
			if day:
				q = q.filter(orig_date__day=day)
	return q[start:end]


def from_tags(tags, page=1, page_range=20):
	start, end = (page-1)*page_range, page*page_range
	q = Post.objects
	for t in tags:
		tag = Tag.objects.get(Q(tag=t) | Q(ascii_tag=t))
		q = q.filter(_tags=tag)
	return q[start:end]
	
