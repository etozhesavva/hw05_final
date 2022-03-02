from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse


from yatube.settings import PAGINATOR_CONST
from ..models import Post, Group, User, Comment, Follow

INDEX = reverse('posts:index')
SLUG = 'Testgroup'
GROUP = reverse('posts:group', kwargs={'slug': SLUG})
SLUG2 = 'Testgroup2'
GROUP2 = reverse('posts:group', kwargs={'slug': SLUG2})
USERNAME = 'User'
USERNAME2 = 'Author'
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
FOLLOW_INDEX = reverse('posts:follow_index')
FOLLOW = reverse('posts:profile_follow', kwargs={'username': USERNAME})
UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': USERNAME})


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
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
        cls.ADD_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[cls.post.id]
        )
        cls.user2 = User.objects.create(username=USERNAME2)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another = Client()
        self.another.force_login(self.user2)

    def post_checking(self, post):
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)

    def test_group_page_show_correct_context(self):
        response_group = self.authorized_client.get(GROUP)
        group_test = response_group.context.get('group')
        self.assertEqual(group_test, self.group)
        self.assertEqual(group_test.slug, self.group.slug)
        self.assertEqual(group_test.title, self.group.title)
        self.assertEqual(group_test.description, self.group.description)

    def test_show_correct_context(self):
        cache.clear()
        urls_names = [
            GROUP,
            INDEX,
            PROFILE,
            FOLLOW_INDEX,
        ]
        for value in urls_names:
            with self.subTest(value=value):
                self.another.get(FOLLOW)
                response = self.another.get(value)
                self.assertEqual(
                    len(response.context['page_obj']), 1
                )
                post = response.context['page_obj'][0]
                self.post_checking(post)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(self.POST_URL)
        post = response.context['post']
        self.post_checking(post)
        self.assertEqual(len(response.context['comments']), 1)
        self.assertEqual(self.comment, response.context.get('comments')[0])

    def test_post_not_in_group2(self):
        response_group = self.authorized_client.get(GROUP2)
        self.assertNotIn(self.post, response_group.context.get('page_obj'))

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(PROFILE)
        self.assertEqual(self.user, response.context.get('author'))

    def test_cache_index_page(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cached_response = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cached_response)

    def test_unfollow_index_page_null(self):
        response = self.another.get(FOLLOW_INDEX)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_follow_user(self):
        self.another.get(FOLLOW)
        follow_exist = Follow.objects.filter(user=self.user2,
                                             author=self.user).exists()
        self.assertTrue(follow_exist)

    def test_unfollow_user(self):
        self.another.get(FOLLOW)
        self.another.get(UNFOLLOW)
        follow_exist = Follow.objects.filter(user=self.user2,
                                             author=self.user).exists()
        self.assertFalse(follow_exist)


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
