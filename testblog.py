# encoding: utf-8

def test_blog():
	from bdblog.models import Post, Word, Tag#,PostDiff
	#p=Post("titolo","testo")
	#p2=Post("titolo","testoaggiornato",orig_date=p.orig_date)
	#dp=PostDiff(p,"")
	#p3=Post("titolo","nuovotesto",orig_date=p2.orig_date)
	#dp2=PostDiff(p2,"")
	#print dp2
	
	p=Post()
	p.title=u"questa è una prova: già, solo una prova"
	p.title=u"this è una prova: già, solo una prova"
	p.text="nothing yet"
	p.save()
	p.tags=["this blog","misc"]
	p.save()
	
	print Word.objects.get(pk="this").num # should == 2
	print Word.objects.get(pk="questa").num # should == 0
	p.title=u"questa è una prova: già, solo una prova"
	p.save()
	print Word.objects.get(pk="this").num # should == 1
	print Word.objects.get(pk="questa").num # should == 1
	
	p.text="changed!"
	p.save()
	
	print Tag.objects.filter(_tag="this blog")[0].post_set.count() #should == 1
	
	newp = Post()
	newp.title=u"this"
	newp._text="bah"
	newp.save()
	
	newp.tags=[u"æble"]
	newp.save()
	
	print Word.objects.get(pk="this").num #should == 2
	
	print Word.objects.get(pk="aeble").num #should == 1
	Tag.objects.filter(_tag=u"æble")[0].post_set.all()[0].delete()
	
	print Word.objects.get(pk="this").num #should == 1
	
	
def test_correct():
	from bdblog.SpellingRedirectMiddleware import SpellingRedirectMiddleware as Spelling
	spelling = Spelling()
	print spelling.correct_month("febbruary") == "february"
	print spelling.correct_month("febbbruary") == "february"
	print spelling.correct_word("blok") == "blog"
	print spelling.correct_word("blokk") == "blog"
	
#import cProfile
#cProfile.runctx("test_correct()", globals(), locals(), filename="profile")

