# conftest.py
import pytest

# Импортируем класс клиента.
from django.test.client import Client
from django.utils import timezone

from datetime import datetime, timedelta

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Комментарий',
        author=author,

    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def pk_for_args(comment):
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment.id,)


@pytest.fixture
def multiple_news():
    news_list = []
    today = datetime.today()
    for i in range(10):
        news = News.objects.create(
            title=f'Заголовок {i+1}',
            text=f'Текст заметки {i+1}',
            date=today - timedelta(days=i + 1)
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def multiple_comments(news, author):
    now = timezone.now()
    for i in range(5):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {i}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=i)
        # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Отредактированный комментарий'}
