from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, form_data, news_detail_url):

    url = news_detail_url
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, form_data, news, news_detail_url, author):

    news_url = news_detail_url
    response = author_client.post(news_url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_user_cant_use_bad_words(
        author_client, news_detail_url, bad_words_data):

    url = news_detail_url
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client, form_data, news_detail_url, comment_edit_url,
        comment):

    url = comment_edit_url
    news_url = news_detail_url
    response = author_client.post(url, form_data)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
    assert updated_comment.created == comment.created


def test_author_can_delete_comment(
        author_client, news_detail_url, comment_delete_url):

    before_deleting = Comment.objects.count()
    assert before_deleting != 0
    url = comment_delete_url
    news_url = news_detail_url
    response = author_client.post(url)
    assertRedirects(response, news_url + '#comments')
    after_deleting = Comment.objects.count()
    assert (before_deleting - 1) == after_deleting


def test_other_user_cant_edit_news(
        not_author_client, form_data, comment_edit_url, comment):

    url = comment_edit_url
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_other_user_cant_delete_comment(not_author_client, comment_delete_url):
    url = comment_delete_url
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
