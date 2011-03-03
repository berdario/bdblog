from models import Post
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
	fields = ['_title', '_text']

admin.site.register(Post, PostAdmin)

