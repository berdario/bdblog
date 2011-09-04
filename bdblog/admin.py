from models import Post
from django.contrib import admin

class PostAdmin(admin.ModelAdmin):
	fields = ['title', 'text']

admin.site.register(Post, PostAdmin)

