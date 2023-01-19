import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post, Group, User
from django.conf import settings
from django.test import Client, TestCase, override_settings
from http import HTTPStatus
from django.urls import reverse

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        # запись
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовые посты'
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_client_post_create(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': self.post.author}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                author=self.post.author,
                group=self.group.pk
            ).exists()
        )

    def test_authorized_client_post_edit(self):
        """Редактирование поста"""
        text_new = 'Отредактированный пост'
        posts_count = Post.objects.count()
        form_data = {
            'text': text_new,
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.pk}))
        # Проверяем, что число постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что запись обновилась
        self.assertTrue(
            Post.objects.filter(
                text=text_new,
                author=self.post.author,
                group=self.group.pk
            ).exists()
        )
