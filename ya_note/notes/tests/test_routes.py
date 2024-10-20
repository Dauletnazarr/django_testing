from http import HTTPStatus

from django.contrib.auth import get_user_model

from .test_base_class import BaseTestCase

User = get_user_model()


class TestRoutes(BaseTestCase):

    def test_page_access(self):
        test_cases = [
            (self.NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_ADD_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (self.DETAIL_URL, self.author_client, HTTPStatus.OK),
            (self.EDIT_URL, self.author_client, HTTPStatus.OK),
            (self.DELETE_URL, self.author_client, HTTPStatus.OK),

            (self.DETAIL_URL, self.other_user_client, HTTPStatus.NOT_FOUND),
            (self.EDIT_URL, self.other_user_client, HTTPStatus.NOT_FOUND),
            (self.DELETE_URL, self.other_user_client, HTTPStatus.NOT_FOUND),
        ]

        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous(self):
        anonymous_test_cases = [
            self.NOTES_LIST_URL,
            self.NOTES_ADD_URL,
            self.NOTES_SUCCESS_URL,
        ]

        for url in anonymous_test_cases:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                redirect_url = f"{self.LOGIN_URL}?next={url}"
                self.assertRedirects(response, redirect_url)
