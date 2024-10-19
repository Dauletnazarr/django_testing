from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.other_user = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.NOTES_LIST_URL = reverse('notes:list')
        cls.NOTES_ADD_URL = reverse('notes:add')
        cls.NOTES_SUCCESS_URL = reverse('notes:success')
        cls.LOGIN_URL = reverse('users:login')
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))

    def setUp(self):
        self.client.force_login(self.author)
        self.anonymous_client = self.client_class()
        self.other_user_client = self.client_class()
        self.other_user_client.force_login(self.other_user)

    def test_page_access(self):
        test_cases = [
            (self.NOTES_LIST_URL, self.client, HTTPStatus.OK),
            (self.NOTES_ADD_URL, self.client, HTTPStatus.OK),
            (self.NOTES_SUCCESS_URL, self.client, HTTPStatus.OK),
            (self.DETAIL_URL, self.client, HTTPStatus.OK),
            (self.EDIT_URL, self.client, HTTPStatus.OK),
            (self.DELETE_URL, self.client, HTTPStatus.OK),

            (self.DETAIL_URL, self.other_user_client, HTTPStatus.NOT_FOUND),
            (self.EDIT_URL, self.other_user_client, HTTPStatus.NOT_FOUND),
            (self.DELETE_URL, self.other_user_client, HTTPStatus.NOT_FOUND),

            (self.NOTES_LIST_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_ADD_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_SUCCESS_URL, self.anonymous_client, HTTPStatus.FOUND),
        ]

        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                if expected_status == HTTPStatus.FOUND:
                    redirect_url = f'{self.LOGIN_URL}?next={url}'
                    self.assertRedirects(response, redirect_url)
                else:
                    self.assertEqual(response.status_code, expected_status)
