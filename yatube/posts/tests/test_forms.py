from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

ONE_POST = 1


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='тест группа',
            slug='test_slug',
            description='Описание группы'
        )
        cls.create_post = Post.objects.create(
            text='Some Text',
            author=cls.user,
            group=cls.group
        )

        cls.post_text_form = {'text': 'Измененный тект', 'group': cls.group.pk}

    def test_create_post_by_user(self):
        """Работа формы зарегистрирванного пользователя"""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Какойто текст'}

        response = self.authorized_client.post(
            reverse('posts:post_create'), data=post_text_form, follow=True)

        self.assertTrue(
            Post.objects.filter(text='Какойто текст').exists())
        self.assertEqual(
            response.status_code, 200)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'NoName'}))
        self.assertEqual(
            Post.objects.count(), posts_count + ONE_POST)

    def test_create_post_by_guest(self):
        """Работа формы не зарегистрирванного пользователя"""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Не текст'}

        response = self.client.post(
            reverse('posts:post_create'), data=post_text_form, follow=True)

        self.assertFalse(
            Post.objects.filter(text='Не текст').exists())
        self.assertEqual(
            response.status_code, 200)
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_post_edit_author(self):
        """Изменение поста зарегистрированным пользователем"""

        response_author = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=self.post_text_form)

        edit_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(response_author.status_code, 302)
        self.assertEqual(edit_post.author.username, 'NoName')
        self.assertEqual(edit_post.text, 'Измененный тект')
        self.assertEqual(edit_post.group.pk, self.group.pk)

    def test_post_edit_guest(self):
        """Изменение поста  не зарегистрированным пользователем"""

        response_guest = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=self.post_text_form)
        edit_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(edit_post.author.username, 'NoName')
        self.assertEqual(edit_post.text, 'Some Text')
        self.assertEqual(edit_post.group.pk, self.group.pk)
