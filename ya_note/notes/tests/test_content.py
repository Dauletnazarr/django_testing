from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestListPage(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Пушкин')
        cls.other_user = User.objects.create(username='Не автор')
        all_notes = [
            Note(
                title=f'Заметка {index + 1}',
                text='Просто текст.',
                author=cls.author,
                slug=f'{index + 1}'
            )
            for index in range(settings.NOTES_COUNT_ON_HOME_PAGE)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, settings.NOTES_COUNT_ON_HOME_PAGE)

    def test_my_notes_only_in_my_list(self):
        self.client.force_login(self.author)

        author_notes = [
            Note.objects.create(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=self.author,
                slug=f'author_{self.author.id}_{index}'
            ) for index in range(5)
        ]

        other_user_notes = [
            Note.objects.create(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=self.other_user,
                slug=f'author_{self.other_user.id}_{index}'
            ) for index in range(5)
        ]

        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']

        for note in object_list:
            self.assertEqual(note.author, self.author)

        for note in other_user_notes:
            self.assertNotIn(note, object_list)


class TestNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пушкин')
        cls.note_create_url = reverse('notes:add',)
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.', author=cls.author
        )
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_create_page_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.note_create_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.note_edit_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)
