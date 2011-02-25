from django.http import HttpResponse
from unidecode import unidecode

def test(request, year=None, month=None, day=None, slug=""):
	return HttpResponse("""test...
	here are the params: <br />
	year: %s <br />
	month: %s <br />
	day: %s <br />
	slug: %s <br />
	unidecoded slug: %s""" % (year, month, day, slug, unidecode(slug)))
