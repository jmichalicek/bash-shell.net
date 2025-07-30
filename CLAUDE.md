## Architecture

- This is a Django project built on Python 3.13.
- This project uses the Wagtail CMS.
- The front end is mostly standard Django templates but views are Wagtail models.
- JavaScript files are kept in the `app/frontend/static/js/` folder and built by webpack into index.js.
- JavaScript code is typically loaded via the static files framework inside Django templates.
- The front end uses PicoCSS 2.0.6 for styling.
- The main database is Postgres.

## Commit Messages

- git commit messages should start with a short sentence describing the overall change or feature being implemented.
- More specific details of the change shoud be added as bullet points with a blank line
  between the bullet points and the leading sentence.
- commit messages should be generated as markdown

## Python

- Python code uses ruff for formatting, sorting imports, and linting.
- Python lines should be 120 characters or less.
- Python dependencies are managed using uv
- code should focus on readability and maintainability first, then performance.
- absolute imports are preferred even for imports from the same package.
- All classes, methods, and functions should include a docstring describing its purpose, parameters, and return value.
- When possible docstrings should include a usage example which can function as a docstring test.
- All Python should include correct type hints.
- Avoid star imports such as `from core import *`
- imports should be sorted according to ruff
- code should be formatted according to ruff
- Do not add a type hint for self.
- Do not use runtime imports unless required to avoid circular imports
- Only imports should be added to the top of a file.
- Add new classes at the end of .py files.
- Add new functions at the end of .py files.
- Add new methods at the bottom of the classes
- Django models go in a models.py
- Django Rest Framework serializers go in a serializers.py
- Never add code before the docstrings
- Never add code before the imports

### Tests

- run tests from the same directory as manage.py using `python manage.py test --parallel`
- Django models should have tests written for `__str__()`
- Django models shouild have tests written for any method added to them.
- Django views should have tests written validating authentication requirements
- Use factory_boy factories to create models in tests.
- WHen using factories use the .create() method because mypy does not understand
  the type hints when just the class is used, such as UserFactory(). Use UserFactory.create() instead.
- When using factories do not specify any fields where a specific value is not required.
  The factories generate randomized, realistic data.
- Test data setup should primarily occur in a test's setUpTestData() classmethod.
- Django views should have tests written validating the template context and that only data which
  should be available to the user is in the context.
- tests for views and viewsets should use django.urls.reverse()
- Tests for Django views should subclass one of the class in the mobelux.core.tests package which provide
  assertHTMLDocumentValid() and assertHTMLFragmentValid() methods.
- assertEqual() should put the expected value first.
- tests for models should go in an app's tests/test_models.py
- tests for views should go in an app's tests/test_views.py
- tests should test happy paths and edge cases
- tests for slow methods and functions which may process a lot of data should, if possible, have data generated which is as small as possible while hitting all paths. This may require a test matrix and subTests with different data to accomplish.
- tests should include type hints

### Django Models

- All models should have a `__str__()` method defined which returns data from the instance which is useful for display to an end user.
- All models should have created_at and updated_at datetime fields where created_at uses auto_now_add=True and updated_at uses auto_now=True
- All models should have a factory_boy factory created for them which generates random data for any field without a default value. This should go in the app's factories.py
- ManyToManyField and ForeignKey should specify a simple and clear related_name. Frequently this is just a pluralized version of the model name in snake_case.

### Django Views

- class based views such as UpdateView and DetailView are preferred over function based views
- very little business logic should be implemented in views so that they are primarily just declarative
  and possibly customizing the queryset.
- ListView should always be paginated unless there is a known, relatively small upper limit to the number of items.

## JavaScript

- This project uses HTMX and so most XMLHTTPRequest type functionality should try to use HTMX.
- JavaScript should be written as ESM modules.
- JavaScript should be put into its own module and imported into index.js or other modules.
- Page specific JavaScript should look for a page specific id on an HTML element and only continue if that is found.
- JavaScript intended to be used in many places or to bind to multiple elements in a page should use a unique data-attribute
  to know which elements to bind to.
- JavaScript should be indented two spaces and use lines of at most 120 characters.
  JavaScript will be automatically formatted using Prettier.
- code should focus on readability and maintainability first, then performance.
- Javascript is compiled using webpack into a single index.js file
- put, post, patch, and delete requests should specify the X-CSRFToken header. This value can be extracted from the csrftoken cookie.

## HTML

- HTML should be indented two spaces.
  HTML will be automatically formatted by djhtml and djade before comitting.
- HTML should use Tailwind Version 4 classes for most styling.
- Forms in Django templates should be rendered using template tags and should make use of django-widget-tweaks to add css classes
  or other attributes to the rendered form elements.

### Django Templates

- In django templates use django template tags and django-widget-tweaks for rendering forms.
- In django template use the `{% static %}` template tag to reference static files such as images, javascript, and css
- In django template use the `{% url %}` template tag for links and form actions rather than hard coded urls.
- The only javascript file from this project which should be included is index.js in the base.html template.
