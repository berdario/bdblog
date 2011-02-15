from berdar.blog.models import Post
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
	fields = ['title', '_text']

admin.site.register(Post, PostAdmin)

