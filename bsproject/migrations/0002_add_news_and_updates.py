# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProjectNews'
        db.create_table('bsproject_projectnews', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bsproject.Project'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('text_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('text_markdown', self.gf('django.db.models.fields.TextField')()),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('bsproject', ['ProjectNews'])


    def backwards(self, orm):
        # Deleting model 'ProjectNews'
        db.delete_table('bsproject_projectnews')


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
        'bsproject.projectnews': {
            'Meta': {'object_name': 'ProjectNews'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bsproject.Project']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'text_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_markdown': ('django.db.models.fields.TextField', [], {})
        },
        'bsproject.versioncontrolsystem': {
            'Meta': {'object_name': 'VersionControlSystem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        }
    }

    complete_apps = ['bsproject']