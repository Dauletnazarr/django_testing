# test_content.py
import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


@pytestmark
def test_news_count(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytestmark
def test_news_order(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytestmark
def test_comments_order(client, multiple_comments, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps, reverse=False)
    assert all_timestamps == sorted_timestamps


@pytestmark
@pytest.mark.parametrize(
    'client_fixture, form_visible',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    ),
)
def test_comment_form_visibility(client_fixture, form_visible, news):
    url = reverse('news:detail', args=[news.id])
    response = client_fixture.get(url)
    form = response.context.get('form')
    assert isinstance(form, CommentForm) == form_visible
