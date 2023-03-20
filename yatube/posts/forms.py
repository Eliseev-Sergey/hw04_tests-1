from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'текст', 'group': 'группа', 'image': 'картинка'}
