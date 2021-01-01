[![Codeship Status for jmichalicek/bash-shell.net](https://app.codeship.com/projects/26e5e670-202c-0137-8746-62ccfb61d2cc/status?branch=master)](https://app.codeship.com/projects/329379)

# bash-shell.net
Main project for http://bash-shell.net/


### Test Fixtures

```
# For blog page tests
python manage.py dumpdata --natural-foreign --indent=2 -e blog.post -e blog.tag accounts sites wagtailcore.site wagtailcore.page wagtailcore.pagerevision

# May need to add wagtailcore.workflowpage, wagtailcore.workflowtask, wagtailcore.task, wagtailcore.workflow, wagtailcore.groupapprovaltask
```

# Tools

## Frameworks
* Django
* Bootstrap 4

## Sites
* https://colormind.io
* https://www.cssfontstack.com/Calibri

## CSS and Icons
* https://simpleicons.org/
* https://bootswatch.com/
