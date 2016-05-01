from __future__ import print_function, unicode_literals, absolute_import
"""
Migrate the old bsblog data to the new blog app
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from ...models import *


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        from bsproject import models as bsproject_models

        HOSTING_SERVICE_MAP = {}

        for hosting_service in bsproject_models.HostingService.objects.all():
            hs, created = HostingService.objects.get_or_create(name=hosting_service.name.strip(),
                                                               defaults={'url': hosting_service.url.strip(),
                                                                         'icon': hosting_service.icon}
            )
            HOSTING_SERVICE_MAP[hosting_service.id] = hs

        for language in bsproject_models.Language.objects.all():
            Language.objects.get_or_create(name=language.name.strip(),
                                           defaults={'description': language.description.strip()}
            )

        for vcs in bsproject_models.VersionControlSystem.objects.all():
            VersionControlSystem.objects.get_or_create(name=vcs.name.strip())

        for old_project in bsproject_models.Project.objects.all().select_related('primary_language'):
            project = Project(
                name=old_project.name,
                description=old_project.description,
                primary_language=Language.objects.get(name=old_project.primary_language.name),
                is_active=True
            )
            project.save()
            langs = Language.objects.filter(name__in=old_project.other_languages.all().values_list('name', flat=True))
            project.other_languages = langs
            Project.objects.filter(id=project.id).update(
                created_date=old_project.created_date, modified_date=old_project.modified_date)

            for hs in old_project.projecthostingservice_set.all():
                if hs.vcs.name.lower() == 'git':
                    vcs = ProjectHostingService.VersionControlSystems.GIT
                elif hs.vcs.name.lower() == 'mercurial':
                    vcs = ProjectHostingService.VersionControlSystems.MERCURIAL
                elif hs.vcs.name.lower() == 'svn':
                    vcs = ProjectHostingService.VersionControlSystems.SVN
                elif hs.vcs.name.lower() == 'cvs':
                    vcs = ProjectHostingService.VersionControlSystems.CVS
                else:
                    vcs = 0

                phs = ProjectHostingService(
                    project=project,
                    project_url=hs.project_url,
                    public_vcs_uri=hs.public_vcs_uri,
                    vcs=vcs,
                    hosting_service=HOSTING_SERVICE_MAP.get(hs.hosting_service.id, None)
                )
                phs.save()

            for old_news in old_project.projectnews_set.all():
                news = ProjectNews(
                    project=project,
                    content=old_news.text_html,
                    title='',
                    is_published=old_news.published
                )
                news.save()
                ProjectNews.objects.filter(id=news.id).update(
                    created_date=old_news.date_created,
                    modified_date=old_news.date_modified
                )
