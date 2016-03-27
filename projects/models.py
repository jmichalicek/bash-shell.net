from __future__ import absolute_import, unicode_literals, division

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify


class HostingService(models.Model):
    """Places that do project and code hosting"""
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=100, blank=True)
    icon = models.ImageField(upload_to='projects/hostimages/', blank=True)
    # lib or django app for api calls/integration?

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name


class Language(models.Model):
    """
    A programming language
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name


class Project(models.Model):
    """
    A software development project
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True,
                                   help_text='A description of the project, history, reason for existence, etc.')
    primary_language = models.ForeignKey(blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='projects'))
    other_languages = models.ManyToManyField(blank=True, on_delete=models.SET_NULL,
                                             related_name='other_language_projects')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    hosting_services = models.ManyToManyField(HostingService, blank=True, through='ProjectHostingService',
                                              help_text='Place the code or project may be hosted',
                                              related_name='projects')
    is_active = models.BooleanField(blank=True, default=False)
    slug = models.SlugField(blank=True, max_length=50, default='')

    class Meta:
        ordering = ('name')

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # duplicate slugs are not properly dealt with anywhere!
            self.slug = slugify(self.title.lower())

        super(Project,self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects_project_detail', args=[self.name])


class ProjectHostingService(models.Model):
    """
    Where a project is hosted
    """

    project = models.ForeignKey('projects.Project', related_name='project_hosting_services')
    hosting_service = models.ForeignKey('projects.HostingService', null=True, on_delete=models.SET_NULL, default=None,
                                        related_name='project_hosting_services')
    project_url = models.URLField(blank=True, help_text='The website URL for the project')
    public_vcs_uri = models.URLField(blank=True, help_text='The URI that can be used to clone, checkout, etc. the project')
    vcs = models.ForeignKey('VersionControlSystem', null=True, blank=True, on_delete=models.SET_NULL, default=None)

    class Meta:
        ordering = ('project', 'hosting_service')

    def __unicode__(self):
        return u'%s: %s' %(self.project, self.hosting_service)


class ProjectNews(models.Model):
    """
    News/blog post related to a project
    """

    project = models.ForeignKey('projects.Project', related_name='project_news')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    is_published = models.BooleanField(db_index=True, default=False, blank=True)

    class Meta:
        order = ('-date_created', )

    def save(self):
        self.text_html = markdown.markdown(self.text_markdown, safe_mode=False)
        super(ProjectNews,self).save()

    def __unicode__(self):
        return u'%s' % self.text_html


class VersionControlSystem(models.Model):
    name = models.CharField(max_length=25)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name
