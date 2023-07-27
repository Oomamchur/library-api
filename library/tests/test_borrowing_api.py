from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse, reverse_lazy

from library.models import Book, Borrowing
from library.serializers import (
    BorrowingListSerializer, BorrowingSerializer, BorrowingListStaffSerializer,
)

BORROWING_URL = reverse("library:borrowing-list")


def detail_url(borrowing_id: int):
    return reverse_lazy("library:borrowing-detail", args=[borrowing_id])


def return_borrowing_url(borrowing_id):
    return detail_url(borrowing_id) + "return"


def test_book(**params) -> Book:
    defaults = {
        "title": "Test title",
        "author": "Test author",
        "inventory": 3,
        "daily_fee": 0.25,
    }
    defaults.update(**params)
    return Book.objects.create(**defaults)


def test_borrowing(**params) -> Borrowing:
    defaults = {
        "book": test_book(),
        "expected_return_date": date.today() + timedelta(days=5),
    }
    defaults.update(**params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@test.com",
            "Test1234",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowing(self) -> None:
        test_borrowing(user=self.user)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_borrowing(self) -> None:
        borrowing = test_borrowing(user=self.user)
        url = detail_url(borrowing.id)
        serializer = BorrowingListSerializer(borrowing)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing(self) -> None:
        book = test_book(title="Kobzar", author="Taras")
        inventory = book.inventory
        payload = {
            "book": book.id,
            "expected_return_date": date.today() + timedelta(days=5),
        }

        response = self.client.post(BORROWING_URL, payload)
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.inventory, inventory - 1)

    def test_filter_active_borrowings(self) -> None:
        borrowing1 = test_borrowing(user=self.user)
        borrowing2 = test_borrowing(user=self.user, actual_return_date=date.today())

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        response = self.client.get(BORROWING_URL, {"is_active": "true"})

        self.assertNotIn(serializer2.data, response.data["results"])
        self.assertIn(serializer1.data, response.data["results"])

    # def test_return_borrowing(self) -> None:
    #     book = test_book(title="Kobzar", author="Taras")
    #     borrowing = test_borrowing(book=book, user=self.user)
    #     inventory = borrowing.book.inventory
    #     print(borrowing.id)
    #     print(borrowing.borrow_date)
    #     url = detail_url(borrowing.id) + "return" return_borrowing_url
    #     print(url)
    #     print(borrowing.actual_return_date)
    #
    #     response = self.client.post(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

        # borrowing.refresh_from_db()
        #
        # print(borrowing.actual_return_date)


class AdminBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            "admin123@admin.com", "test1234", is_staff=True
        )
        self.user = get_user_model().objects.create_user(
            "test123@test.com",
            "Test1234",
        )
        self.client.force_authenticate(self.admin)

    def test_list_borrowing_for_all_users(self) -> None:
        test_borrowing(user=self.user)
        test_borrowing(user=self.admin)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListStaffSerializer(borrowings, many=True)

        response = self.client.get(BORROWING_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filter_borrowings_for_concrete_user(self) -> None:
        borrowing1 = test_borrowing(user=self.user)
        borrowing2 = test_borrowing(user=self.admin)

        serializer1 = BorrowingListStaffSerializer(borrowing1)
        serializer2 = BorrowingListStaffSerializer(borrowing2)

        response = self.client.get(BORROWING_URL, {"user_id": self.user.id})

        self.assertNotIn(serializer2.data, response.data["results"])
        self.assertIn(serializer1.data, response.data["results"])

    def test_update_borrowing(self) -> None:
        borrowing = test_borrowing(user=self.user)
        url = detail_url(borrowing.id)
        exp_date = date.today()
        payload = {"expected_return_date": exp_date}

        response1 = self.client.patch(url, payload)
        response2 = self.client.get(url)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["expected_return_date"], str(payload["expected_return_date"]))

    def test_delete_book(self) -> None:
        borrowing = test_borrowing(user=self.user)
        url = detail_url(borrowing.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
