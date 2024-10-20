from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пушкин Авторов')
        cls.other_user = User.objects.create(username='Хмырь')

        cls.author_client = cls.client_class()
        cls.other_client = cls.client_class()

        cls.author_client.force_login(cls.author)
        cls.other_client.force_login(cls.other_user)

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
        )

        cls.notes_list_url = reverse('notes:list')
        cls.note_edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.note_create_url = reverse('notes:add')


class TestListPage(BaseTestCase):
    def test_my_notes_only_in_my_list(self):
        response = self.author_client.get(self.notes_list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

        response = self.other_client.get(self.notes_list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)


class TestNotePage(BaseTestCase):
    def test_note_pages_have_form(self):
        urls = [self.note_create_url, self.note_edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
