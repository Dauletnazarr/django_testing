import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

NEWS_DETAIL_URL = 'news:detail'
NEWS_EDIT_URL = 'news:edit'
COMMENT_DELETE_URL = 'news:delete'
USERS_LOGIN_URL = 'users:login'
USERS_LOGOUT_URL = 'users:logout'
USERS_SIGNUP_URL = 'users:signup'
NEWS_HOME_URL = 'news:home'
pytestmark = pytest.mark.django_db
lazy_fixture = pytest.lazy_fixture('pk_for_args')


@pytestmark
@pytest.mark.parametrize('name, args', ((
    NEWS_EDIT_URL, lazy_fixture),
    (COMMENT_DELETE_URL, lazy_fixture),),
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    "client_fixture, url_name, args, expected_status",
    [
        ('client', NEWS_DETAIL_URL, lazy_fixture, HTTPStatus.OK),
        ('not_author_client', NEWS_EDIT_URL, lazy_fixture,
         HTTPStatus.NOT_FOUND),
        ('not_author_client', COMMENT_DELETE_URL, lazy_fixture,
         HTTPStatus.NOT_FOUND),
        ('client', USERS_LOGIN_URL, None, HTTPStatus.OK),
        ('client', USERS_LOGOUT_URL, None, HTTPStatus.OK),
        ('client', USERS_SIGNUP_URL, None, HTTPStatus.OK),
        ('client', NEWS_HOME_URL, None, HTTPStatus.OK),
    ]
)
def test_page_availability(
    client_fixture, url_name, args, expected_status, request
):

    client = request.getfixturevalue(client_fixture)
    url = reverse(url_name, args=args if args else ())
    response = client.get(url)
    assert response.status_code == expected_status
