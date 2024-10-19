from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from pytils import translit

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хухры Мухры')
        cls.other_user = User.objects.create(username='Не автор')
        cls.url = reverse('notes:add')
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}

    def setUp(self):
        self.client.force_login(self.author)
        self.anonymous_client = self.client_class()

    def test_logined_user_can_create_note(self):
        Note.objects.all().delete()
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        created_note = Note.objects.get()
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])
        self.assertEqual(created_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        self.anonymous_client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_user_cant_create_two_notes_with_one_slug(self):
        Note.objects.all().delete()
        notes_count_one = Note.objects.count()
        self.form_data['slug'] = 'slug'
        self.client.post(self.url, data=self.form_data)
        notes_count_before = Note.objects.count()
        self.assertNotEqual(notes_count_one, notes_count_before)
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_slug_is_automatically_generated(self):
        notes_count_before = Note.objects.count()
        self.assertEqual(0, notes_count_before)
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(1, notes_count_after)
        created_note = Note.objects.get()
        auto_created_slug = translit.slugify(created_note.title)
        self.assertEqual(created_note.slug, auto_created_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хухры Мухры')
        cls.other_user = User.objects.create(
            username='Не автор', password='password')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, author=cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.data = {'title': cls.NEW_NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def setUp(self):
        self.client.force_login(self.author)
        self.anonymous_client = self.client_class()
        self.other_user_client = self.client_class()
        self.other_user_client.force_login(self.other_user)

    def test_author_can_edit_own_note(self):
        response = self.client.post(
            self.edit_url,
            data=self.data
        )
        get_same_note = Note.objects.get(id=self.note.id)
        self.assertEqual(get_same_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(get_same_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_author_can_delete_own_note(self):
        count_before_deleting = Note.objects.count()
        self.assertNotEqual(count_before_deleting, 0)
        response = self.client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), count_before_deleting - 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_other_user_cannot_edit_note(self):
        response = self.other_user_client.post(
            self.edit_url,
            data={'title': self.NEW_NOTE_TITLE, 'text': self.NEW_NOTE_TEXT})
        get_same_note = Note.objects.get(id=self.note.id)
        self.assertNotEqual(get_same_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_other_user_cannot_delete_note(self):
        notes_count_before = Note.objects.count()
        self.assertNotEqual(notes_count_before, 0)
        response = self.other_user_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
