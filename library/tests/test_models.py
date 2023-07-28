from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from library.models import Book, Borrowing


class ModelsTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@test.com",
            "Test1234",
        )
        self.client.force_authenticate(self.user)

    def test_book_str(self) -> None:
        book = Book.objects.create(
            title="Title", author="Author", inventory=3, daily_fee=0.25
        )

        self.assertEquals(str(book), book.title)

    def test_borrowing_str(self) -> None:
        book = Book.objects.create(
            title="Title", author="Author", inventory=3, daily_fee=0.25
        )
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today(), book=book, user=self.user
        )
        self.assertEquals(
            str(borrowing),
            f"Book: {book.title}, return date: {borrowing.expected_return_date}",
        )
