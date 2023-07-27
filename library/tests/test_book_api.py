from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse, reverse_lazy

from library.models import Book
from library.serializers import BookListSerializer, BookSerializer

BOOK_URL = reverse("library:book-list")


def detail_url(book_id: int):
    return reverse_lazy("library:book-detail", args=[book_id])


def test_book(**params) -> Book:
    defaults = {
        "title": "Test title",
        "author": "Test author",
        "inventory": 3,
        "daily_fee": 0.25,
    }
    defaults.update(**params)
    return Book.objects.create(**defaults)


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@test.com",
            "Test1234",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self) -> None:
        test_book()
        test_book(title="Test2")
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_book(self) -> None:
        book = test_book()
        url = detail_url(book.id)
        serializer = BookSerializer(book)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin123@admin.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self) -> None:
        test_book()
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_update_book(self) -> None:
        book = test_book()
        url = detail_url(book.id)
        payload = {"title": "New Title"}

        response1 = self.client.patch(url, payload)
        response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["title"], payload["title"])

    def test_delete_book(self) -> None:
        book = test_book()
        url = detail_url(book.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
