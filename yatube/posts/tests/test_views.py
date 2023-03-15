from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

# from yatube.posts.utils import NUMBER_POSTS_ON_PAGE

TEST = 1
FIRST_OBJECT = 0
NUMBER_OF_POSTS = 15
NUMBER_POSTS_ON_PAGE = 10
User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='tst_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def test_views_template(self):
        """URL используют правильные шаблоны."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug_name': 'tst_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'NoName'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': TEST}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': TEST}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Index использует правильные данные в контекст."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.select_related('author').all()[FIRST_OBJECT]
        page_obj = response.context['page_obj'][FIRST_OBJECT]
        self.assertIn('page_obj', response.context)
        self.assertEqual(page_obj, post)

    def test_group_list_context(self):
        """Проверка Group list использует правильные данные в контекст."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug_name': 'tst_slug'}))
        post = Post.objects.select_related(
            'author', 'group').filter(group=self.group)[FIRST_OBJECT]

        page_obj = response.context['page_obj'][FIRST_OBJECT]

        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertEqual(page_obj, post)

    def test_profile_context(self):
        """Проверка Profile использует правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'NoName'}))
        post = Post.objects.select_related(
            'author', 'group').filter(author=self.user)[FIRST_OBJECT]
        page_obj = response.context['page_obj'][FIRST_OBJECT]

        self.assertIn('page_obj', response.context)
        self.assertIn('author', response.context)
        self.assertEqual(page_obj, post)

    def test_post_detail_context(self):
        """Проверка Post detail использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))

        post = response.context['post']

        self.assertEqual(post, self.post)

    def test_post_create_context(self):
        """Post create page и post_create использует правильный контекст."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}

        self.assertIn('is_edit', response.context)
        self.assertFalse(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Post create page with post_edit использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        form_field_text = response.context.get('form')['text'].value()
        form_field_group = response.context.get('form')['group'].value()

        self.assertEqual(form_field_text, self.post.text)
        self.assertEqual(form_field_group, self.post.group.pk)
        self.assertIn('is_edit', response.context)
        self.assertTrue(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        for page in range(NUMBER_OF_POSTS):
            Post.objects.create(
                text=f'Test text №{page}',
                author=cls.user,
                group=cls.group,
            )

    def test_paginator_first_page(self):
        """Проверка корректной работы paginator."""
        list_of_check_page = ['/', '/group/test_slug/', '/profile/NoName/']
        for page in list_of_check_page:
            with self.subTest(adress=page):
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), NUMBER_POSTS_ON_PAGE)
                response = self.client.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_OF_POSTS - NUMBER_POSTS_ON_PAGE)
