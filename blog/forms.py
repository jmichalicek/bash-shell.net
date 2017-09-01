from django import forms


from .models import Post


class PostForm(forms.ModelForm):
    """
    Form for editing/creating a Post
    """

    class Meta:
        model = Post
        fields = ('title', 'slug', 'content', 'tags', 'published_date', 'is_published')
