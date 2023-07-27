from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient

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

    def test_book_list(self) -> None:
        test_book()
        test_book(title="Test2")
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_book_retrieve(self) -> None:
        book = test_book()
        url = detail_url(book.id)
        serializer = BookSerializer(book)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_by_title(self) -> None:
        book1 = test_book()
        book2 = test_book(title="Kobzar", author="Taras")

        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)

        response = self.client.get(BOOK_URL, {"title": "kobz"})

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_filter_by_author(self) -> None:
        book1 = test_book()
        book2 = test_book(title="Kobzar", author="Taras")

        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)

        response = self.client.get(BOOK_URL, {"author": "tar"})

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])


class AdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin123@admin.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_book_create(self) -> None:
        test_book()
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)

        response = self.client.get(BOOK_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_book_update(self) -> None:
        book = test_book()
        url = detail_url(book.id)
        payload = {"title": "New Title"}

        response1 = self.client.patch(url, payload)
        response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["title"], payload["title"])

    def test_book_delete(self) -> None:
        book = test_book()
        url = detail_url(book.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
