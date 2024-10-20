from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse

NEWS_DETAIL_URL = lazy_fixture('news_detail_url')
NEWS_EDIT_URL = lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = lazy_fixture('comment_delete_url')
USERS_LOGIN_URL = reverse('users:login')
USERS_LOGOUT_URL = reverse('users:logout')
USERS_SIGNUP_URL = reverse('users:signup')
NEWS_HOME_URL = lazy_fixture('news_home_url')
ANONYMOUS_CLIENT = lazy_fixture('client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('name', ((
    NEWS_EDIT_URL),
    (COMMENT_DELETE_URL),),
)
def test_redirects(client, name):
    login_url = USERS_LOGIN_URL
    url = name
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    "client_fixture, url_name, expected_status",
    [
        (ANONYMOUS_CLIENT, NEWS_DETAIL_URL, HTTPStatus.OK),
        (NOT_AUTHOR_CLIENT, NEWS_EDIT_URL,
         HTTPStatus.NOT_FOUND),
        (NOT_AUTHOR_CLIENT, COMMENT_DELETE_URL,
         HTTPStatus.NOT_FOUND),
        (ANONYMOUS_CLIENT, USERS_LOGIN_URL, HTTPStatus.OK),
        (ANONYMOUS_CLIENT, USERS_LOGOUT_URL, HTTPStatus.OK),
        (ANONYMOUS_CLIENT, USERS_SIGNUP_URL, HTTPStatus.OK),
        (ANONYMOUS_CLIENT, NEWS_HOME_URL, HTTPStatus.OK),
    ]
)
def test_page_availability(
    client_fixture, url_name, expected_status
):

    url = url_name
    response = client_fixture.get(url)
    assert response.status_code == expected_status
