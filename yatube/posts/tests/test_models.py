from django.test import TestCase

from posts.models import Group, Post, User, Comment


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug='Test',
            description='Test'
        )
        cls.post = Post.objects.create(
            text='Test',
            author=cls.user,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст Комментария'
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(self.comment.text, str(self.comment))
