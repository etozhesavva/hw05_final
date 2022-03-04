from django.test import TestCase
from django.urls import reverse

SLUG = 'testgroup'
USERNAME = 'TestAuthor'
POST_ID = 1


class ReverseTests(TestCase):
    urls_names = [
        ['/', 'posts:index', []],
        ['/create/', 'posts:create', []],
        [f'/group/{SLUG}/', 'posts:group', [SLUG]],
        [f'/profile/{USERNAME}/', 'posts:profile', [USERNAME]],
        [f'/posts/{POST_ID}/', 'posts:post_detail', [POST_ID]],
        [f'/posts/{POST_ID}/edit/', 'posts:post_edit', [POST_ID]],
        [f'/posts/{POST_ID}/comment/', 'posts:add_comment', [POST_ID]],
        ['/follow/', 'posts:follow_index', []],
        [f'/profile/{USERNAME}/follow/', 'posts:profile_follow', [USERNAME]],
        [f'/profile/{USERNAME}/unfollow/', 'posts:profile_unfollow', [USERNAME]]
    ]

    def test_url_uses_correct_reverse(self):
        for direct_url, route, params in self.urls_names:
            self.assertEqual(
                direct_url, reverse(f'{route}',
                                    args=params)
            )
