from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # неавторизованный клиент
        cls.guest_client = Client()
        # авторизованый клиент
        cls.user = User.objects.create(username='User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # группа в БД
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # пост в БД
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='100'
        )

    def test_authorized_pages_url_exists_at_desired_location(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/posts/100/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_guest_pages_url_exists_at_desired_location(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/User/': HTTPStatus.OK,
            '/posts/100/': HTTPStatus.OK,
            '/posts/100/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for address, status in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_post_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/User/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/posts/100/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
