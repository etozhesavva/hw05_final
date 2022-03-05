from django.test import TestCase
from django.urls import reverse
from django.conf import settings

SLUG = 'testgroup'
USERNAME = 'TestAuthor'
POST_ID = 1


class ReverseTests(TestCase):
    urls_names = [
        ['/', 'index', []],
        ['/create/', 'create', []],
        [f'/group/{SLUG}/', 'group', [SLUG]],
        [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
        [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
        [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
        [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
        ['/follow/', 'follow_index', []],
        [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
        [f'/profile/{USERNAME}/unfollow/',
         'profile_unfollow', [USERNAME]]
    ]

    def test_url_uses_correct_reverse(self):
        for direct_url, route, params in self.urls_names:
            self.assertEqual(
                direct_url, reverse(f'{ settings.POST_PATH }:{route}',
                                    args=params)
            )
