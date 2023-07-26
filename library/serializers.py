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
    book = BookListSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)
        if attrs["book"].inventory == 0:
            raise serializers.ValidationError(
                "There is no such book available now"
            )
        return data

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        borrowing.book.inventory -= 1
        borrowing.book.save()
        return borrowing

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )
