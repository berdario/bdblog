# encoding: utf-8

from blog.models import Post, Word, Tag#,PostDiff
#p=Post("titolo","testo")
#p2=Post("titolo","testoaggiornato",orig_date=p.orig_date)
#dp=PostDiff(p,"")
#p3=Post("titolo","nuovotesto",orig_date=p2.orig_date)
#dp2=PostDiff(p2,"")
#print dp2

p=Post()
p.title=u"questa è una prova: già, solo una prova"
p.title=u"this è una prova: già, solo una prova"
p._text="nothing yet"
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

print Tag.objects.filter(tag="this blog")[0].post_set.count() #should == 1

newp = Post()
newp.title=u"this"
newp._text="bah"
newp.save()

newp.tags=["bah"]
newp.save()

print Word.objects.get(pk="this").num #should == 2

Tag.objects.filter(tag="bah")[0].post_set.all()[0].delete()

print Word.objects.get(pk="this").num #should == 1
