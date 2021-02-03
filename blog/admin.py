from django.contrib import admin

from blog.models import BlogPage

# I want to see what kind of nightmare this results in in the djangoadmin since this
# is a wagtail Page model
admin.site.register(BlogPage)
