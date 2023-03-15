from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

ONE_POST = 1


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='тест группа',
            slug='test_slug',
            description='Описание группы'
        )

        cls.second_group = Group.objects.create(
            title='тест группа #2',
            slug='test_slug_second',
            description='Описание группы'
        )

        cls.create_post = Post.objects.create(
            text='Some Text',
            author=cls.user,
            group=cls.group
        )

        cls.post_text_form = {'text': 'Измененный тект', 'group': cls.group.pk}

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_by_user(self):
        """Работа формы зарегистрирванного пользователя"""

        posts_count = Post.objects.count()

        set_ids_before = set(Post.objects.values_list('id', flat=True))

        response = self.authorized_client.post(
            reverse('posts:post_create'), data=self.post_text_form, follow=True)

        set_ids_after = set(Post.objects.values_list('id', flat=True))
        id_post = list(set(set_ids_after) - set(set_ids_before))[0]

        post = Post.objects.select_related('group', 'author').get(pk=id_post)

        self.assertEqual(self.post_text_form['text'], post.text)
        self.assertEqual(self.post_text_form['group'], post.group.pk)
        self.assertEqual(self.user, post.author)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), posts_count + ONE_POST)

    def test_create_post_by_guest(self):
        """Работа формы не зарегистрирванного пользователя"""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Не текст'}

        response = self.client.post(
            reverse('posts:post_create'), data=post_text_form, follow=True)

        self.assertEqual(
            response.status_code, 200)
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_post_edit_author(self):
        """Изменение поста зарегистрированным пользователем"""

        post_text_form = {'text': 'Измененный тект',
                          'group': self.second_group.pk}

        response_author = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=post_text_form)

        edit_post = Post.objects.select_related(
            'group', 'author').get(pk=self.create_post.id)

        self.assertEqual(response_author.status_code, 302)
        self.assertEqual(edit_post.author,  self.create_post.author)
        self.assertEqual(edit_post.text, 'Измененный тект')
        self.assertEqual(edit_post.group.pk, self.second_group.pk)

    def test_post_edit_guest(self):
        """Изменение поста  не зарегистрированным пользователем"""

        response_guest = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.create_post.id}),
            data=self.post_text_form)
        edit_post = Post.objects.select_related(
            'group', 'author').get(pk=self.create_post.id)

        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(edit_post.author, self.create_post.author)
        self.assertEqual(edit_post.text, 'Some Text')
        self.assertEqual(edit_post.group.pk, self.group.pk)
