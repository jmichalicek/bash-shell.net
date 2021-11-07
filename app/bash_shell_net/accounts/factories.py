import factory
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    is_staff = False
    is_superuser = None
    email = factory.Sequence(lambda n: f'user{n}@example.org')
    username = factory.Sequence(lambda n: 'user{n}')

    class Meta:
        model = 'accounts.User'

    @factory.post_generation
    def setuser_password(obj, create, extracted, **kwargs):
        obj.set_password('password')
        obj.save()
