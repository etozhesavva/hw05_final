from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from yatube.settings import PAGINATOR_CONST
from ..models import Post, Group, User, Comment, Follow

INDEX = reverse('posts:index')
SLUG = 'Testgroup'
GROUP = reverse('posts:group', kwargs={'slug': SLUG})
SLUG2 = 'Testgroup2'
GROUP2 = reverse('posts:group', kwargs={'slug': SLUG2})
USERNAME = 'User'
USERNAME2 = 'Author'
PROFILE = reverse('posts:profile', args=[USERNAME])
FOLLOW_INDEX = reverse('posts:follow_index')
FOLLOW = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW = reverse('posts:profile_unfollow', args=[USERNAME])
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user2 = User.objects.create(username=USERNAME2)
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='testt',
            slug=SLUG,
            description='testd',
        )
        cls.group_2 = Group.objects.create(
            title="testt2",
            slug=SLUG2,
            description="testd2",
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded

        )
        cls.POST_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст Комментария'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2.force_login(cls.user2)

    def post_checking(self, post):
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_group_page_show_correct_context(self):
        response_group = self.authorized_client.get(GROUP)
        group = response_group.context.get('group')
        self.assertEqual(group, self.group)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)

    def test_show_correct_context(self):
        cache.clear()
        urls_names = [
            GROUP,
            INDEX,
            PROFILE,
            FOLLOW_INDEX,
        ]
        self.authorized_client2.get(FOLLOW)
        for value in urls_names:
            with self.subTest(value=value):
                response = self.authorized_client2.get(value)
                self.assertEqual(
                    len(response.context['page_obj']), 1
                )
                post = response.context['page_obj'][0]
                self.post_checking(post)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(self.POST_URL)
        post = response.context['post']
        comments = post.comments.all()
        self.post_checking(post)
        self.assertEqual(len(comments), 1)
        self.assertEqual(self.comment, comments[0])

    def test_unfollow_index_page_null_or_post_not_in_group2(self):
        urls = [
            GROUP2, 
            FOLLOW_INDEX,
        ]

        for value in urls:
            response = self.authorized_client.get(value)
            self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(PROFILE)
        self.assertEqual(self.user, response.context.get('author'))

    def test_cache_index_page(self):
        page = self.authorized_client.get(INDEX).content
        Post.objects.create(
            text='text', author=self.user, group=self.group
        )
        self.assertEqual(
            page, self.authorized_client.get(INDEX).content)
        cache.clear()
        self.assertNotEqual(
            page, self.authorized_client.get(INDEX).content)

    def test_follow_user(self):
        self.authorized_client2.get(FOLLOW)
        self.assertTrue(Follow.objects.filter(user=self.user2,
                                              author=self.user).exists())

    def test_unfollow(self):
        Follow.objects.create(user=self.user2, author=self.user)
        self.authorized_client.get(UNFOLLOW)
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        Post.objects.bulk_create([Post(author=cls.user,
                                       text=str(i))
                                  for i in range(PAGINATOR_CONST)])

    def test_page_count_records(self):
        cache.clear()
        response = self.client.get(INDEX)
        self.assertEqual(
            len(response.context['page_obj']), PAGINATOR_CONST
        )
