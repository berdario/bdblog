from django.http import HttpResponse
from unidecode import unidecode
from re import sub

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
