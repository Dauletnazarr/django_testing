from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from pytils import translit

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

    def test_logined_user_can_create_note(self):
        self.client.force_login(self.author)
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_create_two_notes_with_one_slug(self):
        self.client.force_login(self.author)
        self.form_data['slug'] = 'slug'
        self.client.post(self.url, data=self.form_data)
        notes_count_before = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_slug_is_automatically_generated(self):
        self.client.force_login(self.author)
        self.client.post(self.url, data=self.form_data)
        # Получаем последнюю созданную заметку
        created_note = Note.objects.last()
        auto_created_slug = translit.slugify(created_note.title)
        # Ожидаемое значение slug
        self.assertEqual(created_note.slug, auto_created_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Хухры Мухры')
        cls.other_user = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, author=cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_edit_own_note(self):
        self.client.force_login(self.author)
        response = self.client.post(
            self.edit_url,
            data={'title': self.NEW_NOTE_TITLE, 'text': self.NEW_NOTE_TEXT}
        )
        self.note.refresh_from_db()  # Обновляем экземпляр заметки из базы
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_author_can_delete_own_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)
        # Проверяем, что заметка удалена
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_other_user_cannot_edit_note(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            self.edit_url,
            data={'title': self.NEW_NOTE_TITLE, 'text': self.NEW_NOTE_TEXT})
        self.note.refresh_from_db()
        # Убедимся, что заголовок не изменился
        self.assertNotEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_other_user_cannot_delete_note(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.delete_url)
        # Проверяем, что заметка не удалена
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
