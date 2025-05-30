import factory
from accounts.models import User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    is_staff = False
    is_superuser = None
    email = factory.Sequence(lambda n: f"user{n}@example.org")
    username = factory.Sequence(lambda n: f"user{n}")

    class Meta:
        model = User

    @factory.post_generation
    def setuser_password(obj: User, create, extracted, **kwargs):
        obj.set_password("password")
        obj.save()
