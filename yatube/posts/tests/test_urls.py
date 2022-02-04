from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        guest_client = self.guest_client
        authorized_client = self.authorized_client

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
            '/posts/13/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_pages_response_guest(self):
        template_address = {
            '/': 200,
            '/group/slug-slug/': 200,
            '/profile/auth/': 200,
            '/posts/13/': 200,
            '/create/': 302,
            '/posts/13/edit/': 302
        }
        for address, code in template_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_response_authorized_user(self):
        template_address = {
            '/': 200,
            '/create/': 200,
            '/group/slug-slug/': 200,
            '/profile/auth/': 200,
            '/posts/13/': 200,
            '/posts/13/edit/': 200
        }
        for address, code in template_address.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_edit_not_author(self):
        User2 = User.objects.create_user(username='auth2')
        Post.objects.create(text='123', author=User2, pk=12)
        response = self.authorized_client.get('/posts/12/edit/')
        self.assertEqual(response.status_code, 302)
