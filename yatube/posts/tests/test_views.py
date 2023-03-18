from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import User, Group, Post


TEST_NUM = 1
FIRST_OBJECT = 0
NUMBER_OF_POSTS = 15
NUMBER_POSTS_ON_FIRST_PAGE = 10
NUMBER_POSTS_ON_SECOND_PAGE = 5


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')
        cls.another_user = User.objects.create(username='AnotherName')

        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another_slug',
            description='Другое тестовое описание'
        )

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

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_template(self):
        """URL используют правильные шаблоны."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug_name': 'tst_slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'NoName'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': TEST_NUM}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': TEST_NUM}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Index использует правильные данные в контекст."""
        response = self.authorized_client.get(reverse('posts:index'))
        page_obj = response.context['page_obj'][FIRST_OBJECT]

        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)

    def test_group_list_context(self):
        """Проверка Group list использует правильные данные в контекст."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug_name': 'tst_slug'}))

        page_obj = response.context['page_obj'][FIRST_OBJECT]

        self.assertEqual(page_obj, self.post)
        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)
        self.assertNotEqual(page_obj.group, self.another_group)

    def test_profile_context(self):
        """Проверка Profile использует правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'NoName'}))

        page_obj = response.context['page_obj'][FIRST_OBJECT]

        self.assertEqual(page_obj.author, self.post.author)
        self.assertEqual(page_obj.group, self.post.group)
        self.assertEqual(page_obj.id, self.post.id)
        self.assertEqual(page_obj.text, self.post.text)

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

    def test_post_in_profile_on_first_position(self):
        """Проверка, что пост в profile попадает на первую позицию"""
        self.test_post = Post.objects.create(
            text='Этот пост должен быть первым',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}))
        page_obj = response.context['page_obj'][FIRST_OBJECT]
        self.assertEqual(self.test_post, page_obj)
        print(page_obj.text)

    def test_post_in_group_list_on_first_position(self):
        """Проверка, что пост в group_list попадает на первую позицию"""
        self.test_post = Post.objects.create(
            text='Этот пост должен быть первым в группе',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug_name': self.test_post.group.slug}))
        page_obj = response.context['page_obj'][FIRST_OBJECT]
        self.assertEqual(self.test_post, page_obj)


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
        list_of_paginator_page = [('?page=1',
                                   NUMBER_POSTS_ON_FIRST_PAGE),
                                  ('?page=2',
                                   NUMBER_POSTS_ON_SECOND_PAGE)]
        for page in list_of_check_page:
            with self.subTest(adress=page):
                for pag in list_of_paginator_page:
                    with self.subTest(adress=pag):
                        response = self.client.get(page + pag[0])
                        self.assertEqual(
                            len(response.context['page_obj']), pag[1])

