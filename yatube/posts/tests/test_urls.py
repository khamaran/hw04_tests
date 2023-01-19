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

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_detail_url_exists_at_desired_location(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/<str:username>/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/User/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница /posts/100/ доступна любому пользователю."""
        response = self.guest_client.get('/posts/100/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_url_exists_at_desired_location(self):
        """Страница /posts/100/edit/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/posts/100/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна только авторизированному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Страница /unexisting_page/ ведёт к ошибке 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

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
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
