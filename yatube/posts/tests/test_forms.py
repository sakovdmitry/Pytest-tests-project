from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Post


User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
            'pk': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок',
                pk=1
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый заголовок',
            'pk': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        form_data = {
            'text': 'Тестовый отредактированный',
            'pk': 1
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый отредактированный',
                pk=1
            ).exists()
        )
