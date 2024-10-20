from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хухры Мухры')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.other_user = User.objects.create(username='Не автор')
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)

        cls.anonymous_client = cls.client_class()

        cls.form_data = {
            'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 'slug': 'slug'}
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT,
            author=cls.author, slug='slug'
        )

        cls.NOTES_LIST_URL = reverse('notes:list')
        cls.NOTES_ADD_URL = reverse('notes:add')
        cls.NOTES_SUCCESS_URL = reverse('notes:success')
        cls.LOGIN_URL = reverse('users:login')
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
