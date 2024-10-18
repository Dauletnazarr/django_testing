import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from http import HTTPStatus


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('name, args', ((
    'news:edit', pytest.lazy_fixture('pk_for_args')),
    ('news:delete', pytest.lazy_fixture('pk_for_args')),),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args')),
    ),
)
def test_not_author_cant_edit_delete_comments(not_author_client, name, args):
    expected_url = HTTPStatus.NOT_FOUND
    url = reverse(name, args=args)
    response = not_author_client.get(url)
    assert response.status_code == expected_url


@pytest.mark.parametrize('name',
                         ('users:login', 'users:logout', 'users:signup'))
def test_pages_availability_for_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
