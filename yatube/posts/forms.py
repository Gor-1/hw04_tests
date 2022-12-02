from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        label = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_text = {
            'text': 'Пост который хотите добавить или редактировать',
            'group': 'Из уже существующих'
        }
