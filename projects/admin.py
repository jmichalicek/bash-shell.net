from django.contrib import admin

from models import *


#inlines
class ProjectHostingServiceInline(admin.StackedInline):
    model = ProjectHostingService
    extra = 1


#admins
class HostingServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','primary_language','created_date', 'modified_date')
    search_fields = ['name', 'description']
    list_filter = ('primary_language',)
    fieldsets = (
        (None,{'fields': ['name','description','primary_language',
                          'other_languages', 'created_date','modified_date']}),
    )
    readonly_fields = ['created_date', 'modified_date']
    inlines = [ProjectHostingServiceInline]


class ProjectHostingServiceAdmin(admin.ModelAdmin):
    list_display = ('project', 'hosting_service', 'vcs')
    list_filter = ['hosting_service', 'vcs']
    search_fields = ['project__name']


class ProjectNewsAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'created_date', 'modified_date', 'is_published')
    list_filter = ('project',)
    list_editable = ['is_published']
    search_fields = ['project__name', 'title']
    fieldsets = (
        (None, {'fields': ['title', 'project', 'content', 'is_published']}),
    )


admin.site.register(HostingService, HostingServiceAdmin)
admin.site.register(Language)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectHostingService, ProjectHostingServiceAdmin)
admin.site.register(ProjectNews, ProjectNewsAdmin)
admin.site.register(VersionControlSystem)
