from berdar.blog.models import Post#,PostDiff
#p=Post("titolo","testo")
#p2=Post("titolo","testoaggiornato",orig_date=p.orig_date)
#dp=PostDiff(p,"")
#p3=Post("titolo","nuovotesto",orig_date=p2.orig_date)
#dp2=PostDiff(p2,"")
#print dp2

p=Post()
p.title=u"questa è una prova: già, solo una prova"
p._text="nothing yet"
p.rating=0
p.save()

