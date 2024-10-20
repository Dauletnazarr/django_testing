from notes.forms import NoteForm
from .test_base_class import BaseTestCase


class TestListPage(BaseTestCase):
    def test_my_notes_only_in_my_list(self):
        test_cases = [
            (self.author_client, self.assertIn),
            (self.other_user_client, self.assertNotIn)
        ]

        for client, check_func in test_cases:
            response = client.get(self.NOTES_LIST_URL)
            object_list = response.context['object_list']

            with self.subTest(client=client):
                check_func(self.note, object_list)


class TestNotePage(BaseTestCase):
    def test_note_pages_have_form(self):
        urls = [self.NOTES_ADD_URL, self.EDIT_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
