# test_content.py
import pytest
from django.conf import settings

from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, multiple_news):
    # Адрес страницы получаем через reverse():
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # print(f'Количество записей в News: {News.objects.count()}')
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # print(all_dates)
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # print(sorted_dates)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, multiple_comments, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех комментариев.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps, reverse=False)
    # print(f'Количество записей в Comment: {Comment.objects.count()}')
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, form_visible",
    (
        (None, False),
        ("author_client", True),
    ),
)
def test_comment_form_visibility(request, client_fixture, form_visible, news):
    if client_fixture:
        client = request.getfixturevalue(client_fixture)
    else:
        client = request.getfixturevalue("client")
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    if form_visible:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
