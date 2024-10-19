from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Пушкин")
        cls.notes = [
            Note(
                title=f"Заметка {index + 1}",
                text="Просто текст.",
                author=cls.author,
                slug=f"note-{index + 1}"
            ) for index in range(5)
        ]
        Note.objects.bulk_create(cls.notes)
        cls.notes_list_url = reverse('notes:list')
        cls.note_edit_url = reverse('notes:edit', args=[cls.notes[0].id])

    def setUp(self):
        self.client.force_login(self.author)

    def test_my_notes_only_in_my_list(self):
        response = self.client.get(self.notes_list_url)
        object_list = response.context['object_list']
        for note in object_list:
            self.assertEqual(note.author, self.author)


class TestNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пушкин')
        cls.note_create_url = reverse('notes:add',)
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.', author=cls.author
        )
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def setUp(self):
        self.client.force_login(self.author)

    def test_note_pages_have_form(self):
        urls = [self.note_create_url, self.note_edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
