from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='User')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_login_url_exists_at_desired_location(self):
        """Страница /login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_url_exists_at_desired_location(self):
        """Страница /signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url_exists_at_desired_location(self):
        """Страница /logout/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_exists_at_desired_location(self):
        """Страница /password_change/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_exists_at_desired_location(self):
        """Страница /password_change/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_done_exists_at_desired_location(self):
        """Страница /reset/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_exists_at_desired_location(self):
        """Страница /password_reset/done/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_id_exists_at_desired_location(self):
        """Страница /reset/test/test/ доступна только авторизированному
        пользователю."""
        response = self.authorized_client.get('/auth/reset/test/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_exists_at_desired_location(self):
        """Страница /password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/test/test/': 'users/password_reset_confirm.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }
        for address, template in templates_url.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
