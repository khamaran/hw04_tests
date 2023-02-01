import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from django import forms

from posts.models import Post, Group, Follow

test_posts: int = 15
User = get_user_model()

# Папка для медиафайлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
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
        # Тест-картинка
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # посты в БД
        for post in range(test_posts):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовые посты',
                image=uploaded
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'User'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                'posts/post_create.html'
            ),
        }
        for reverse_name, template, in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        post_image = Post.objects.last().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_first_page_index_page_contains_ten_records(self):
        # Проверка: количество постов на первой странице равно 10.
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_page_contains_five_records(self):
        # Проверка: количество постов на первой странице равно 5.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertIn('group', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIn('posts', response.context)
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание')
        self.assertEqual(response.context.get('group').slug, 'test-slug')
        post_image = Post.objects.last().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_first_page_group_posts_page_contains_ten_records(self):
        # Проверка: количество постов на первой странице равно 10.
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_posts_page_contains_five_records(self):
        # Проверка: количество постов на первой странице равно 5.
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'User'})
        )
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn('posts', response.context)
        self.assertIn('posts_count', response.context)
        self.assertIn('page_obj', response.context)
        post_image = Post.objects.last().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_first_page_profile_page_contains_ten_records(self):
        # Проверка: количество постов на первой странице равно 10.
        response = self.client.get(reverse('posts:profile',
                                   kwargs={'username': 'User'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_page_contains_five_records(self):
        # Проверка: количество постов на первой странице равно 5.
        response = self.client.get(reverse('posts:profile',
                                   kwargs={'username': 'User'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        self.assertIn('post', response.context)
        self.assertIn('posts_count', response.context)
        post_image = Post.objects.last().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={"post_id": self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_index_cache(self):
        """Кэш на главной странице работает правильно."""
        cache.clear()
        # Первый запрос: пост создан, но его нет в кэше
        self.authorized_client.get(reverse('posts:index'))
        cache_post = Post.objects.create(
            text="Тест-кэш",
            author=self.user
        )
        response_2 = self.authorized_client.get(reverse('posts:index'))
        # Пост создан, но его нет во втором запросе,
        self.assertNotIn(cache_post.text, response_2.content.decode())
        # Чистим кэш
        cache.clear()
        # Делаем третий запрос
        response_3 = self.authorized_client.get(reverse('posts:index'))
        # Удаляем пост
        cache_post.delete()
        # Пост должен быть в кэше в третьем запросе, хотя он удалён
        self.assertIn(cache_post.text, response_3.content.decode())
        # Чистим кэш
        cache.clear()
        # Делаем 4 запрос
        response_4 = self.authorized_client.get(reverse('posts:index'))
        # Кэщ очищен, поста нет
        self.assertNotIn(cache_post.text, response_4.content.decode())


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = Client()
        cls.following = Client()
        cls.user_follower = User.objects.create(username='follower')
        cls.user_following = User.objects.create(username='following')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тест поста в ленте подписчиков'
        )
        cls.follower.force_login(cls.user_follower)
        cls.following.force_login(cls.user_following)

    def test_follow(self):
        self.follower.get(reverse('posts:profile_follow',
                                  kwargs={'username':
                                          self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        self.follower.get('/follow/')
        self.follower.get(reverse('posts:profile_unfollow',
                                  kwargs={'username':
                                          self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscriber(self):
        """Новая запись автора появляется в ленте подписчиков,
        и не появляется в ленте подписок не подписчиков."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.follower.get('/follow/')
        post_text = response.context['page_obj'][0].text
        self.assertEqual(post_text, 'Тест поста в ленте подписчиков')
        # проверка, что запись не появилась у неподписанного пользователя
        response = self.following.get('/follow/')
        self.assertNotEqual(response, 'Тест поста в ленте подписчиков')
