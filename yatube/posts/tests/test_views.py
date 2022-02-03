from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            pk=13,
            author=cls.user,
            text='Тестовая группа тестовая группа',
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={'slug': 'slug-slug'})),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'auth'})),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': 13})),
            'posts/post_create.html': (
                reverse('posts:post_edit', kwargs={'post_id': 13})),
            'posts/post_create.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_post_group_profile_show_correct_context(self):
        """Шаблоны index, post_group, profile сформированы с правильным контекстом."""
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group_list = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'slug-slug'}))
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))

        context_index = response_index.context['page_obj'][0]
        context_group_list = response_group_list.context['page_obj'][0]
        context_profile = response_profile.context['page_obj'][0]

        tags = [context_index, context_group_list, context_profile]

        for value in tags:
            group_title = value.group.title
            author_name = value.author.username
            post_text = value.text
            self.assertEqual(group_title, 'Тестовая группа')
            self.assertEqual(author_name, 'auth')
            self.assertEqual(post_text, 'Тестовая группа тестовая группа')

    def test_index_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 13}))
        self.assertEqual(response.context.get(
            'post').author.username, 'auth')
        self.assertEqual(response.context.get(
            'post').text, 'Тестовая группа тестовая группа')
        self.assertEqual(response.context.get('post').pk, 13)

    def test_create_edit_show_correct_context(self):
        """Шаблоны create и post edit сформированы с правильным контекстом."""
        response_create = self.authorized_client.get(
            reverse('posts:post_create'))
        response_edit = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 13}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_create = response_create.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_create, expected)
                form_field_edit = response_edit.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_edit, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        tests_posts_text = [str(i) for i in range(13)]
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-slug',)
        for i in tests_posts_text:
            Post.objects.create(author=cls.user, text=i, group=cls.group)

    def test_first_page_contains_ten_records(self):
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group_posts = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'slug-slug'}))
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        responses = [response_index, response_group_posts, response_profile]
        for value in responses:
            response = value
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response_index = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        response_group_posts = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'slug-slug'}) + '?page=2')
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        responses = [response_index, response_group_posts, response_profile]
        for value in responses:
            response = value
            self.assertEqual(len(response.context['page_obj']), 3)
