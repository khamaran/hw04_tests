from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class UserURLTests(TestCase):
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

    def test_login_url_exists_at_desired_location(self):
        """Страница /login/ доступна любому пользователю."""
        response = self.guest_client.get('/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_url_exists_at_desired_location(self):
        """Страница /signup/ доступна любому пользователю."""
        response = self.guest_client.get('/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url_exists_at_desired_location(self):
        """Страница /logout/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_exists_at_desired_location(self):
        """Страница /password_change/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_exists_at_desired_location(self):
        """Страница /password_change/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_done_exists_at_desired_location(self):
        """Страница /reset/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_exists_at_desired_location(self):
        """Страница /password_reset/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_id_exists_at_desired_location(self):
        """Страница /reset/test/test/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/reset/test/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_exists_at_desired_location(self):
        """Страница /password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_urls_redirect_anonymous(self):
        """URL-адреса перенаправляют анонимного пользователя."""
        # Шаблоны по адресам
        templates_url_names = {
            'logout/': 'users/logged_out.html',
            '/signup/': 'users/signup.html',
            '/login/': 'users/login.html',
            'password_change/done/': 'users/password_change_done.html',
            'password_change/': 'users/password_change_form.html',
            'reset/done/': 'users/password_reset_complete.html',
            'password_reset/done/': 'users/password_reset_done.html',
            '/reset/test/test/': 'users/password_reset_confirm.html',
            'password_reset/': 'users/password_reset_form.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(template, follow=True)
                self.assertRedirects(response, '/users/login/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'logout/': 'users/logged_out.html',
            '/signup/': 'users/signup.html',
            '/login/': 'users/login.html',
            'password_change/done/': 'users/password_change_done.html',
            'password_change/': 'users/password_change_form.html',
            'reset/done/': 'users/password_reset_complete.html',
            'password_reset/done/': 'users/password_reset_done.html',
            '/reset/test/test/': 'users/password_reset_confirm.html',
            'password_reset/': 'users/password_reset_form.html',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
