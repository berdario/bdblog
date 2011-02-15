from berdar.blog.models import Post, PostDiff
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
	fields = ['title', '_text']

admin.site.register(Post, PostAdmin)

