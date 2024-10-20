from django.contrib.auth import get_user_model
from django.test import Client, TestCase
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
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.anonymous_client = cls.client_class()
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 'slug': 'slug'}
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT,
            author=cls.author, slug='slug'
        )

    def test_logined_user_can_create_note(self):
        Note.objects.all().delete()
        self.author_client.post(self.url, data=self.form_data)
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
        notes_count_before = Note.objects.count()
        self.author_client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_slug_is_automatically_generated(self):
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.assertEqual(0, notes_count_before)
        del self.form_data['slug']
        self.author_client.post(self.url, data=self.form_data)
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
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user = User.objects.create(username='Не автор')
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)
        cls.form_data = {
            'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 'slug': 'slug'}
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT,
            author=cls.author, slug='slug'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.data = {'title': cls.NEW_NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_author_can_edit_own_note(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.data
        )
        get_same_note = Note.objects.get(id=self.note.id)
        self.assertEqual(get_same_note.title, self.data['title'])
        self.assertEqual(get_same_note.text, self.data['text'])
        self.assertEqual(get_same_note.author, self.author)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_author_can_delete_own_note(self):
        count_before_deleting = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), count_before_deleting - 1)
        self.assertRedirects(response, reverse('notes:success'))

    def test_other_user_cannot_edit_note(self):
        self.other_user_client.post(
            self.edit_url,
            data={'title': self.NEW_NOTE_TITLE, 'text': self.NEW_NOTE_TEXT})
        get_same_note = Note.objects.get(id=self.note.id)
        self.assertEqual(get_same_note.title, self.note.title)
        self.assertEqual(get_same_note.text, self.note.text)
        self.assertEqual(get_same_note.author, self.author)
        self.assertEqual(get_same_note.id, self.note.id)

    def test_other_user_cannot_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.other_user_client.post(self.delete_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
