from django.http import HttpResponse
from unidecode import unidecode
from re import sub
from datetime import date

from models import from_tags, get_post, get_posts

months = {"jan":1, "feb":2, "mar":3, "apr":4, "may": "5", "jun":6,
	"jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
	"january":1, "february":2, "march":3, "april":4, "june":6,
	"july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}

def test(request, year=None, month=None, day=None, slug="", admin=False):
	return HttpResponse("""test...
	here are the params: <br />
	year: %s <br />
	month: %s <br />
	day: %s <br />
	slug: %s <br />
	admin: %s <br />
	unidecoded slug: %s""" % (year, month, day, slug, admin, unidecode(slug)))
	
def test_tags(request, tags, admin=False, separator="\."):
	return HttpResponse("""
	tags: %s <br />
	admin: %s <br/>
	""" % ([sub(separator," ",tag) for tag in tags.split("+")], admin))
	
def index(request, page, admin=False):
	return HttpResponse("""TODO""")

def post(request, slug, year, month, day, admin=False):
	d = None
	if year and month and day:
		month = _handle_verbose_month(month)
		d = date(int(year), month, int(day))
	p = get_post(slug, d)
	return HttpResponse("""title: %s <br />
	text: %s""" % (p.title, p.text))

def posts(request, year, month, day, page, admin=False):
	month = _handle_verbose_month(month)
	post_list = get_posts(year, month, day, page if page else 1)
	return HttpResponse(
	"".join(["""<p>title: %s <br />
	text: %s<p/>""" % (p.title, p.text) for p in post_list])
	)
		
def tags(request, tags, page, separator="\.", admin=False):
	tag_list = [sub(separator," ",tag) for tag in tags.split("+")]
	post_list = from_tags(tag_list, page if page else 1)
	return HttpResponse(
	"".join(["""<p>title: %s <br />
	text: %s<p/>""" % (p.title, p.text) for p in post_list])
	)

def _handle_verbose_month(month):
	if month:
		try:
			return int(month)
		except ValueError:
			try:
				return months[month]
			except KeyError:
				raise UnknownMonth(month)

class UnknownMonth(Exception):
	def __init__(self, month):
		self.month = month
