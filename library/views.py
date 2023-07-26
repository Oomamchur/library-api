from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from library.models import Book, Borrowing
from library.permissions import IsAdminOrReadOnly
from library.serializers import (
    BookSerializer,
    BookListSerializer,
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"] and self.request.user.is_staff:
            return BorrowingSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action in ("update", "partial_update"):
            return BorrowingSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active:
            if is_active.lower().capitalize() == "True":
                queryset = queryset.filter(actual_return_date=None)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        elif user_id:
            queryset = queryset.filter(user_id=int(user_id))

        return queryset

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminUser()]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
