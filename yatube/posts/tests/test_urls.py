from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_author = User.objects.create_user(username='test_author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)

        cls.post = Post.objects.create(
            text='Текстовый текст',
            author=cls.test_author
        )
        cls.group = Group.objects.create(
            title='Тесторвая группа',
            slug='test_slag',
            description='Тестовое описание'
        )

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_location(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get('/group/test_slag/')
        self.assertEqual(resource.status_code, 200)

    def test_profile_url_lacation(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get('/profile/test_author/')
        self.assertEqual(resource.status_code, 200)

    def test_post_id_url_location(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(resource.status_code, 200)

    def test_edit_url_location(self):
        """Страница / доступна автору поста."""
        resource = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(resource.status_code, 200)

    def test_create_url_location(self):
        """Страница / доступна авторизованому пользователю."""
        resource = self.authorized_client.get('/create/')
        self.assertEqual(resource.status_code, 200)

    def test_404_url_locations(self):
        """Не доступная страница"""
        resource = self.client.get('/404/')
        self.assertEqual(resource.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/group/test_slag/': 'posts/group_list.html',
            '/profile/test_author/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/': 'posts/index.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
