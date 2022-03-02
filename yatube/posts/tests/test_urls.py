from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('posts:index')
NEW_POST = reverse('posts:create')
USERNAME = 'TestAuthor'
USERNAME2 = 'TestAuthor2'
AUTH_LOGIN = reverse('login')
SLUG = 'testgroup'
GROUP_URL = reverse('posts:group', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
LOGIN_CREATE_POST = f'{AUTH_LOGIN}?next={NEW_POST}'


class UrlsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Test',
            slug=SLUG,
            description='Test'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
            group=cls.group
        )
        cls.user2 = User.objects.create(username=USERNAME2)
        cls.POST_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id])
        cls.LOGIN_EDIT_POST = f'{AUTH_LOGIN}?next={cls.POST_EDIT_URL}'

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.another = Client()
        self.another.force_login(self.user2)

    def test_urls_status_code(self):
        urls_names = [
            [self.POST_EDIT_URL, self.another, 302],
            [INDEX, self.guest, 200],
            [NEW_POST, self.guest, 302],
            [GROUP_URL, self.guest, 200],
            [self.POST_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.author, 200],
            [NEW_POST, self.author, 200],
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url, client=client, status=status):
                self.assertEqual(client.get(url).status_code, status)

    def test_urls_uses_correct_template(self):
        template_urls_names = [
            ['posts/index.html', INDEX],
            ['posts/create_post.html', NEW_POST],
            ['posts/group_list.html', GROUP_URL],
            ['posts/post_detail.html', self.POST_URL],
            ['posts/profile.html', PROFILE_URL],
            ['posts/create_post.html', self.POST_EDIT_URL]
        ]
        for template, url in template_urls_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.author.get(url),
                                        template)

    def test_redirect_urls_correct(self):
        urls = [
            [NEW_POST, self.guest, LOGIN_CREATE_POST],
            [self.POST_EDIT_URL, self.guest,
             self.LOGIN_EDIT_POST],
            [self.POST_EDIT_URL, self.another, self.POST_URL],
        ]
        for url, client, redirect in urls:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url, follow=True), redirect)
