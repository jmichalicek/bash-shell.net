# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HostingService'
        db.create_table('bsproject_hostingservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=100, blank=True)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('bsproject', ['HostingService'])

        # Adding model 'Language'
        db.create_table('bsproject_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('bsproject', ['Language'])

        # Adding model 'Project'
        db.create_table('bsproject_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_markdown', self.gf('django.db.models.fields.TextField')()),
            ('primary_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bsproject.Language'], null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('bsproject', ['Project'])

        # Adding M2M table for field other_languages on 'Project'
        db.create_table('bsproject_project_other_languages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['bsproject.project'], null=False)),
            ('language', models.ForeignKey(orm['bsproject.language'], null=False))
        ))
        db.create_unique('bsproject_project_other_languages', ['project_id', 'language_id'])

        # Adding model 'ProjectHostingService'
        db.create_table('bsproject_projecthostingservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bsproject.Project'])),
            ('hosting_service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bsproject.HostingService'])),
            ('project_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('public_vcs_uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('vcs', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bsproject.VersionControlSystem'], null=True, blank=True)),
        ))
        db.send_create_signal('bsproject', ['ProjectHostingService'])

        # Adding model 'VersionControlSystem'
        db.create_table('bsproject_versioncontrolsystem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('bsproject', ['VersionControlSystem'])


    def backwards(self, orm):
        # Deleting model 'HostingService'
        db.delete_table('bsproject_hostingservice')

        # Deleting model 'Language'
        db.delete_table('bsproject_language')

        # Deleting model 'Project'
        db.delete_table('bsproject_project')

        # Removing M2M table for field other_languages on 'Project'
        db.delete_table('bsproject_project_other_languages')

        # Deleting model 'ProjectHostingService'
        db.delete_table('bsproject_projecthostingservice')

        # Deleting model 'VersionControlSystem'
        db.delete_table('bsproject_versioncontrolsystem')


    models = {
        'bsproject.hostingservice': {
            'Meta': {'object_name': 'HostingService'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'blank': 'True'})
        },
        'bsproject.language': {
            'Meta': {'object_name': 'Language'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'bsproject.project': {
            'Meta': {'object_name': 'Project'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_markdown': ('django.db.models.fields.TextField', [], {}),
            'hosting_services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['bsproject.HostingService']", 'symmetrical': 'False', 'through': "orm['bsproject.ProjectHostingService']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'other_languages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'project_other_languages_set'", 'to': "orm['bsproject.Language']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'db_index': 'True'}),
            'primary_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bsproject.Language']", 'null': 'True', 'blank': 'True'})
        },
        'bsproject.projecthostingservice': {
            'Meta': {'object_name': 'ProjectHostingService'},
            'hosting_service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bsproject.HostingService']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bsproject.Project']"}),
            'project_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'public_vcs_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'vcs': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bsproject.VersionControlSystem']", 'null': 'True', 'blank': 'True'})
        },
        'bsproject.versioncontrolsystem': {
            'Meta': {'object_name': 'VersionControlSystem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        }
    }

    complete_apps = ['bsproject']