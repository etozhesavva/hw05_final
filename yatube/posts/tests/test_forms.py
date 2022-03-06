import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

LOGIN_URL = reverse('login')
NEW_POST = reverse('posts:create')
INDEX = reverse('posts:index')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
LOGIN_CREATE_POST = f'{LOGIN_URL}?next={NEW_POST}'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user2 = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Test',
            slug='Tests',
            description='Testss'
        )
        cls.group2 = Group.objects.create(
            title='Test2',
            slug='Tests2',
            description='Testss2',
        )
        cls.group3 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='Tests3'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text',
            group=cls.group
        )
        cls.POST_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[cls.post.id])
        cls.PROFILE_URL = reverse(
            'posts:profile',
            args=[cls.user.username]
        )
        cls.ADD_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id])
        cls.REDIRECT_COMMENT_URL = (LOGIN_URL + '?next=' + cls.ADD_COMMENT_URL)
        cls.REDIRECT_EDIT_URL = (LOGIN_URL + '?next=' + cls.POST_EDIT_URL)
        cls.POST_URL = reverse(
            'posts:post_detail',
            args=[cls.post.id])
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user2)
        cls.guest = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create(self):
        posts = Post.objects.all()
        posts.delete()
        UPLOADED = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        data = {
            'text': 'Текст формы',
            'group': self.group.id,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            NEW_POST,
            data=data,
            follow=True
        )
        post = response.context['page_obj'][0]
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(post.text, data['text'])
        self.assertEqual(data['group'], post.group.id)
        self.assertEqual(post.author, self.user)
        self.assertEqual(
            post.image.name,
            f'{settings.POST_PATH}/{UPLOADED.name}'
        )
        self.assertRedirects(response, self.PROFILE_URL)

    def test_new_post_show_correct_context(self):
        urls = [
            NEW_POST,
            self.POST_EDIT_URL
        ]
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.Field,
                       'image': forms.fields.ImageField
                       }
        for url in urls:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_edit_post(self):
        UPLOADED = SimpleUploadedFile(
            name='sm.gif',
            content=GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'hi!',
            'group': self.group2.id,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data, follow=True
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(form_data['group'], post.group.id)
        self.assertEqual(post.image.name,
                         f'{settings.POST_PATH}/{UPLOADED.name}')
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_URL)

    def test_comment_save(self):
        form_data = {
            'text': 'Текст',
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data, follow=True
        )
        post = response.context['post']
        comments = post.comments.all()
        self.assertEqual(len(comments), 1)
        comment = comments[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_anonimys_create_post(self):
        Post.objects.all().delete()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'text',
            'group': self.group2.id,
            'image': uploaded
        }
        response = self.guest.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, LOGIN_CREATE_POST)
        self.assertEqual(Post.objects.count(), 0)

    def test_anonimys_create_comment(self):
        self.post.comments.all().delete()
        form_data = {
            'text': 'test'
        }
        response = self.guest.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.REDIRECT_COMMENT_URL)
        self.assertEqual(self.post.comments.count(), 0)

    def test_anonimys_or_non_author_post_edit(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'TEST',
            'group': self.group3.id,
            'image': uploaded
        }
        clients = [
            [self.guest, self.REDIRECT_EDIT_URL],
            [self.another, self.POST_URL]
        ]
        count = Post.objects.count()
        for client, url in clients:
            with self.subTest(client=client, url=url):
                response = client.post(
                    self.POST_EDIT_URL,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, url)
                post = Post.objects.get(pk=self.post.id)
                self.assertEqual(count, Post.objects.count())
                self.assertEqual(self.post.text, post.text)
                self.assertEqual(self.post.author, post.author)
                self.assertEqual(self.post.group, post.group)
