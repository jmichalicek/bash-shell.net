import factory
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    is_staff = False
    is_superuser = None
    email = factory.Sequence(lambda n: 'user%n@example.org' % n)
    username = factory.Sequence(lambda n: 'user%n' % n)

    class Meta:
        model = 'accounts.User'

    @factory.post_generation
    def setuser_password(obj, create, extracted, **kwargs):
        obj.set_password('password')
        obj.save()
