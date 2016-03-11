from django.db import models

import markdown


class HostingService(models.Model):
    """Places that do project and code hosting"""
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=100, blank=True)
    icon = models.ImageField(upload_to='bsproject/hostimages/', blank=True)
    # lib or django app for api calls/integration?

    def __unicode__(self):
        return u'%s' %self.name


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return u'%s' %self.name


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True,
                                   help_text='A description of the project, history, reason for existence, etc.')
    description_markdown = models.TextField(help_text='A description of the project, history, reason for existence, etc. Accepts html and markdown.')
    primary_language = models.ForeignKey('Language', db_index=True, blank=True, null=True)
    other_languages = models.ManyToManyField('Language', db_index=True, blank=True, null=True,
                                             related_name='project_other_languages_set')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    hosting_services = models.ManyToManyField(HostingService, blank=True, through='ProjectHostingService',
                                              help_text='Place the code or project may be hosted')

    def __unicode__(self):
        return u'%s' %self.name

    def save(self, *args, **kwargs):
        self.description = markdown.markdown(self.description_markdown, safe_mode=False)
        super(Project,self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('bsproject_project', [self.name])


class ProjectHostingService(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    hosting_service = models.ForeignKey(HostingService, db_index=True)
    project_url = models.URLField(blank=True, help_text='The website URL for the project')
    public_vcs_uri = models.URLField(blank=True, help_text='The URI that can be used to clone, checkout, etc. the project')
    vcs = models.ForeignKey('VersionControlSystem', db_index=True, null=True, blank=True)

    def __unicode__(self):
        return u'%s: %s' %(self.project, self.hosting_service)

class ProjectNews(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    text_html = models.TextField(blank=True)
    text_markdown = models.TextField()
    published = models.BooleanField(db_index=True, default=False)

    def save(self):
        self.text_html = markdown.markdown(self.text_markdown, safe_mode=False)
        super(ProjectNews,self).save()

    def __unicode__(self):
        return u'%s' %self.text_html

class VersionControlSystem(models.Model):
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return u'%s' %self.name
