from django.core import serializers
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.core.files.images import get_image_dimensions
from django.views.generic.edit import CreateView, UpdateView
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from unidecode import unidecode
from re import sub
from datetime import date
from collections import Iterable
from itertools import izip

json = serializers.get_serializer('json')()

from models import from_tags, get_post, get_posts, PostForm, PostFormSet

months = dict((month, n % 12) for n, month in enumerate([
	"jan", "feb", "mar", "apr", "may", "jun",
	"jul", "aug", "sep", "oct", "nov", "dec",
	"january", "february", "march", "april", "june",
	"july", "august", "september", "october", "november", "december"])) 

def json_or_template(template):
	def outer(view):
		def wrapped(*args, **kwargs):
			request = args[0]
			result, context = view(*args, **kwargs)
			context.update(csrf(request))
			if isinstance(result, Iterable):
				context['post_list'] = [(post, form, reverse(update_post, args=[p.pk])) for p,(post, form) in izip(result, context['post_list'])]
			else:
				context['target'] = reverse(update_post, args=[result.pk])
				result = [result]
			if _accept_json(request):
				return HttpResponse(json.serialize(result), mimetype='application/json')
			else:
				return render_to_response(template, context, context_instance=RequestContext(request))
		return wrapped
	return outer

@json_or_template('blog')
def index(request, page, admin=False):
	form = PostForm()
	publish = reverse(publish_post)
	bare_posts = get_posts(page=page if page else 1)
	post_list = izip(bare_posts, PostFormSet(queryset=bare_posts))
	return bare_posts, locals() 

@json_or_template('single_post')
def post(request, slug, year, month, day, admin=False):
	d = None
	if year and month and day:
		month = _handle_verbose_month(month)
		d = date(int(year), month, int(day))
	p = get_post(slug, d)
	form = PostForm(instance=p)
	return p, locals()

@json_or_template('posts')
def posts(request, year, month, day, page, admin=False):
	month = _handle_verbose_month(month)
	bare_posts = get_posts(year, month, day, page if page else 1)
	post_list = izip(bare_posts, PostFormSet(queryset=bare_posts))
	return bare_posts, locals()

@json_or_template('posts')
def tags(request, tags, page, separator="\.", admin=False):
	tag_list = [sub(separator," ",tag) for tag in tags.split("+")]
	bare_posts = from_tags(tag_list, page if page else 1)
	post_list = izip(bare_posts, PostFormSet(queryset=bare_posts))
	return bare_posts, locals()

class ThumbMixin(object):
	def get_success_url(self):
		obj = self.object or self.get_object()
		obj.mug.flush()
		if get_image_dimensions(obj.mug) != (100, 100):
			return reverse(update_post, args=[obj.pk])
		return super(ThumbMixin, self).get_success_url()

class PublishPost(ThumbMixin, CreateView):
	form_class = PostForm
	template_name = "validate"

publish_post = PublishPost.as_view()

class UpdatePost(ThumbMixin, UpdateView):
	form_class = PostForm
	model = form_class.Meta.model
	template_name = "validate"

update_post = UpdatePost.as_view()

def _handle_verbose_month(month):
	if month:
		try:
			return int(month)
		except ValueError:
			try:
				return months[month]
			except KeyError:
				raise UnknownMonth(month)

def _accept_json(request):
	return 'application/json' in request.META.get('HTTP_ACCEPT_ENCODING', '')

class UnknownMonth(Exception):
	def __init__(self, month):
		self.month = month
	
	def __str__(self):
		return self.month
