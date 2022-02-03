from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-slug',
        )
        cls.post = Post.objects.create(
            pk=13,
            author=cls.user,
            text='Тестовая группа тестовая группа',
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        guest_client = TaskURLTests.guest_client
        authorized_client = TaskURLTests.authorized_client

        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/13/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = guest_client.get(address)
                self.assertTemplateUsed(response, template)

        templates_url_names = {
            'posts/post_create.html': '/posts/13/edit/',
            'posts/post_create.html': '/create/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = authorized_client.get(address)
                self.assertTemplateUsed(response, template)

        response = guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
