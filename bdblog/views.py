from django.http import HttpResponse
from django.shortcuts import render_to_response
from unidecode import unidecode
from re import sub
from datetime import date
from django.core import serializers
json = serializers.get_serializer('json')()

from models import from_tags, get_post, get_posts, PostForm

months = {"jan":1, "feb":2, "mar":3, "apr":4, "may": "5", "jun":6,
	"jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
	"january":1, "february":2, "march":3, "april":4, "june":6,
	"july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
	
def index(request, page, admin=False):
	if 'application/json' in request.META['HTTP_ACCEPT_ENCODING']:
		return HttpResponse("""TODO""", mimetype='application/json')
	else:
		return render_to_response('main', locals())

def post(request, slug, year, month, day, admin=False):
	d = None
	if year and month and day:
		month = _handle_verbose_month(month)
		d = date(int(year), month, int(day))
	p = get_post(slug, d)
	if _accept_json(request):
		return HttpResponse(json.serialize([p]), mimetype='application/json')
	else:
		return render_to_response('single_post', locals())

def posts(request, year, month, day, page, admin=False):
	month = _handle_verbose_month(month)
	post_list = get_posts(year, month, day, page if page else 1)
		
	if _accept_json(request):
		return HttpResponse(json.serialize(post_list), mimetype='application/json')
	else:
		return render_to_response('posts', locals())
		
def tags(request, tags, page, separator="\.", admin=False):
	tag_list = [sub(separator," ",tag) for tag in tags.split("+")]
	post_list = from_tags(tag_list, page if page else 1)
	if _accept_json(request):
		return HttpResponse(json.serialize(post_list), mimetype='application/json')
	else:
		return render_to_response('posts', locals())

def publish_post(request, slug):
	return HttpResponse("TODO")
	
def test_modelform(request):
	f = PostForm()
	return HttpResponse("""<form action="/blog/publish" method="post">
%s
<input type="Submit" value="GO"
</form>
	""" % (f.as_p(),))

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
