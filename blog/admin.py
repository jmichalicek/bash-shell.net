from __future__ import absolute_import, unicode_literals

from django.contrib import admin
#from django.contrib.contenttypes import generic

from .models import Post, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date', 'updated_date', 'published_date', 'is_published')
    search_fields = ['title', 'content', 'tags',]
    list_filter = ('is_published', 'published_date', 'created_date', 'updated_date')
    fieldsets = (
        (None,{'fields': ['title', 'slug', 'content', 'tags', 'published_date', 'is_published']}),
        (None, {'fields': ['created_date', 'updated_date']})
    )
    prepopulated_fields = {"slug" : ['title']}
    readonly_fields = ('created_date', 'updated_date')


    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class TagAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name',)
    #search_fields = ['name',]
    #fieldsets = (
    #    (None,{'fields' : ('name',)}),
    #)

admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
