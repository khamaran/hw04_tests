from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
# from django import forms

from posts.models import Post, Group

User = get_user_model()


class UserViewsTests(TestCase):
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

    def test_users_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset_complete'):
            'users/password_reset_complete.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': '<uidb64>', 'token': 'token'}):
            'users/password_reset_confirm.html',
            reverse('users:password_reset_form'):
            'users/password_reset_form.html',
        }
        for reverse_name, template, in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
