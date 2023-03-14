from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group

        self.assertEqual(post.text[:15], post.__str__())
        self.assertEqual(group.title, group.__str__())

    def test_models_verbose_name(self):
        """Проверяем verbose_name в post и group"""
        post = PostModelTest.post
        help_text_for_text = post._meta.get_field('text').help_text
        help_text_for_group = post._meta.get_field('group').help_text
        self.assertEqual(
            help_text_for_text,
            'Введите текст поста'
        )
        self.assertEqual(
            help_text_for_group,
            'Группа, к которой будет отновится пост'
        )
