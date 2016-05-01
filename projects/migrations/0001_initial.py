# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HostingService'
        db.create_table(u'projects_hostingservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=100, blank=True)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'projects', ['HostingService'])

        # Adding model 'Language'
        db.create_table(u'projects_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'projects', ['Language'])

        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('primary_language', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'projects', on_delete=models.SET_NULL, default=None, to=orm['projects.Language'], blank=True, null=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.SlugField')(default=u'', max_length=50, blank=True)),
        ))
        db.send_create_signal(u'projects', ['Project'])

        # Adding M2M table for field other_languages on 'Project'
        m2m_table_name = db.shorten_name(u'projects_project_other_languages')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'projects.project'], null=False)),
            ('language', models.ForeignKey(orm[u'projects.language'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'language_id'])

        # Adding model 'ProjectHostingService'
        db.create_table(u'projects_projecthostingservice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'project_hosting_services', to=orm['projects.Project'])),
            ('hosting_service', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name=u'project_hosting_services', null=True, on_delete=models.SET_NULL, to=orm['projects.HostingService'])),
            ('project_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('public_vcs_uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('vcs', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'projects', ['ProjectHostingService'])

        # Adding model 'ProjectNews'
        db.create_table(u'projects_projectnews', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'project_news', to=orm['projects.Project'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'projects', ['ProjectNews'])

        # Adding model 'VersionControlSystem'
        db.create_table(u'projects_versioncontrolsystem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'projects', ['VersionControlSystem'])


    def backwards(self, orm):
        # Deleting model 'HostingService'
        db.delete_table(u'projects_hostingservice')

        # Deleting model 'Language'
        db.delete_table(u'projects_language')

        # Deleting model 'Project'
        db.delete_table(u'projects_project')

        # Removing M2M table for field other_languages on 'Project'
        db.delete_table(db.shorten_name(u'projects_project_other_languages'))

        # Deleting model 'ProjectHostingService'
        db.delete_table(u'projects_projecthostingservice')

        # Deleting model 'ProjectNews'
        db.delete_table(u'projects_projectnews')

        # Deleting model 'VersionControlSystem'
        db.delete_table(u'projects_versioncontrolsystem')


    models = {
        u'projects.hostingservice': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'HostingService'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'projects.language': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Language'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'projects.project': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Project'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hosting_services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'projects'", 'blank': 'True', 'through': u"orm['projects.ProjectHostingService']", 'to': u"orm['projects.HostingService']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'other_languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'other_language_projects'", 'blank': 'True', 'to': u"orm['projects.Language']"}),
            'primary_language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'projects'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['projects.Language']", 'blank': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'})
        },
        u'projects.projecthostingservice': {
            'Meta': {'ordering': "(u'project', u'hosting_service')", 'object_name': 'ProjectHostingService'},
            'hosting_service': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'project_hosting_services'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['projects.HostingService']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'project_hosting_services'", 'to': u"orm['projects.Project']"}),
            'project_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'public_vcs_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'vcs': ('django.db.models.fields.IntegerField', [], {})
        },
        u'projects.projectnews': {
            'Meta': {'ordering': "(u'-created_date',)", 'object_name': 'ProjectNews'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'project_news'", 'to': u"orm['projects.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.versioncontrolsystem': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'VersionControlSystem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        }
    }

    complete_apps = ['projects']