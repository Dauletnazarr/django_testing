# test_routes.py
import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('notes:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# test_routes.py
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# def test_note_exists(note):
#     notes_count = Note.objects.count()
#     # Общее количество заметок в БД равно 1.
#     assert notes_count == 1
#     # Заголовок объекта, полученного при помощи фикстуры note,
#     # совпадает с тем, что указан в фикстуре.
#     assert note.title == 'Заголовок'


# # Обозначаем, что тесту нужен доступ к БД.
# # Без этой метки тест выдаст ошибку доступа к БД.
# @pytest.mark.django_db
# def test_empty_db():
#     notes_count = Note.objects.count()
#     # В пустой БД никаких заметок не будет:
#     assert notes_count == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, note, expected_status
):
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# @pytest.mark.parametrize(
#     # Вторым параметром передаём note_object,
#     # в котором будет либо фикстура с объектом заметки, либо None.
#     'name, note_object',
#     (
#         ('notes:detail', pytest.lazy_fixture('note')),
#         ('notes:edit', pytest.lazy_fixture('note')),
#         ('notes:delete', pytest.lazy_fixture('note')),
#         ('notes:add', None),
#         ('notes:success', None),
#         ('notes:list', None),
#     ),
# )
# # Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
# def test_redirects(client, name, note_object):
#     login_url = reverse('users:login')
#     # Формируем URL в зависимости от того, передан ли объект заметки:
#     if note_object is not None:
#         url = reverse(name, args=(note_object.slug,))
#     else:
#         url = reverse(name)
#     expected_url = f'{login_url}?next={url}'
#     response = client.get(url)
#     # Ожидаем, что со всех проверяемых страниц анонимный клиент
#     # будет перенаправлен на страницу логина:
#     assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
