from django.test import TestCase
from django.urls import reverse

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
        [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]]
    ]

    def test_url_uses_correct_reverse(self):
        for direct_url, route, params in self.urls_names:
            self.assertEqual(
                direct_url, reverse(f'posts:{route}',
                                    args=params)
            )
