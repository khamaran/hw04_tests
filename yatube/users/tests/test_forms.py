from posts.models import User
from django.test import Client, TestCase
from http import HTTPStatus
from django.urls import reverse


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='User')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_guest_client_signup(self):
        """Валидная форма создает аккаунт"""
        users = User.objects.count()
        form_data = {
            'first_name': 'Testa',
            'last_name': 'Testova',
            'username': 'User2',
            'email': 'test2@test.ru',
            'password1': 'password_test_2',
            'password2': 'password_test_2'
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:index'))
        # Проверяем, что на 1 пользователя стало больше
        print(users)
        self.assertEqual(User.objects.count(), users + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            User.objects.filter(
                first_name='Testa',
                last_name='Testova',
                username='User2',
                email='test2@test.ru',
            ).exists()
        )
