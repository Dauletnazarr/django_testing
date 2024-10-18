from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from http import HTTPStatus

import pytest

from news.forms import WARNING, BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    # Через анонимный клиент пытаемся создать комментарий:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 комментариев.
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, form_data, news):
    news_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(news_url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert new_comment.text == form_data['text']
    # Вроде бы здесь нарушен принцип "один тест - одна проверка";
    # но если хоть одна из этих проверок провалится -
    # весь тест можно признать провалившимся, а последующие невыполненные
    # проверки не внесли бы в отчёт о тесте ничего принципиально важного.


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(response, 'form', 'text', errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, form_data, news, comment):
    # Получаем адрес страницы редактирования заметки:
    url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки:
    response = author_client.post(url, form_data)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    # Обновляем объект заметки note: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты заметки соответствуют обновлённым:
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    assert Comment.objects.count() == 1
    response = author_client.post(url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_news(not_author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
