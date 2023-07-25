from rest_framework import serializers

from library.models import Book, Borrowing


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "daily_fee", "inventory")


class BookListSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author")


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)

    # class Meta:
    #     model = Borrowing
    #     fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")

