from datetime import date

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
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs)
        if attrs["book"].inventory == 0:
            raise serializers.ValidationError(
                "There is no such book available now"
            )
        if attrs["expected_return_date"] < date.today():
            raise serializers.ValidationError(
                "Return date can't be earlier than today"
            )
        return data

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        borrowing.book.inventory -= 1
        borrowing.book.save()
        return borrowing

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookListSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingListStaffSerializer(BorrowingListSerializer):
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


class BorrowingDetailSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data) -> object:
        return_date = validated_data.get(
            "expected_return_date", instance.expected_return_date
        )
        if return_date < date.today():
            raise serializers.ValidationError(
                "Return date can't be earlier than today"
            )
        if instance.actual_return_date:
            raise serializers.ValidationError("Book is already returned")
        instance.expected_return_date = return_date
        instance.save()

        return instance

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")
        read_only_fields = ("book",)
