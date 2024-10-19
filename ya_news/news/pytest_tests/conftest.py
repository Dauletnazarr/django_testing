import pytest

from django.conf import settings

from django.test.client import Client

from django.utils import timezone

from datetime import datetime, timedelta

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Комментарий',
        author=author,
    )


@pytest.fixture
def pk_for_args(comment):
    return (comment.id,)


@pytest.fixture
def multiple_news():
    news_list = []
    today = datetime.today()
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Заголовок {i+1}',
            text=f'Текст заметки {i+1}',
            date=today - timedelta(days=i + 1)
        )
        news_list.append(news)
    News.objects.bulk_create(news_list)


@pytest.fixture
def multiple_comments(news, author):
    now = timezone.now()
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Отредактированный комментарий'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст {BAD_WORDS[0]}, еще текст'}
