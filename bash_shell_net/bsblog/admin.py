from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Post, Category
from taxonomy.admin import TaxonomyMapInline

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','created_date','category','published')
    search_fields = ['title', 'text_markdown','category',]
    list_filter = ('created_date','published')
    fieldsets = (
        (None,{'fields': ['title','text_markdown','category','created_date','slug','published']}),
    )
    prepopulated_fields = {"slug" : ['title']}

    inlines = [TaxonomyMapInline,]

    def save_model(self, request, obj, form, change):
        obj.user_profile = request.user.get_profile()
        obj.save() 


class CategoryAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name',)
    #search_fields = ['name',]
    #fieldsets = (
    #    (None,{'fields' : ('name',)}),
    #)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
