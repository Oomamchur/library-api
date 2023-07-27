from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from library.models import Book, Borrowing
from library.permissions import IsAdminOrReadOnly
from library.serializers import (
    BookSerializer,
    BookListSerializer,
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingListStaffSerializer,
    BorrowingDetailSerializer,
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by title(ex. ?title=Harry)",
            ),
            OpenApiParameter(
                "author",
                type=OpenApiTypes.STR,
                description="Filter by author(ex. ?author=Orwell)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            if self.request.user.is_staff:
                return BorrowingListStaffSerializer
            return BorrowingListSerializer

        if self.action in ("update", "partial_update"):
            return BorrowingDetailSerializer

        return BorrowingSerializer

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by is_active(ex. ?is_active=true)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user_id(ex. ?user_id=3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminUser()]

        return super().get_permissions()

    @action(methods=["POST"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date is None:
            borrowing.actual_return_date = date.today()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

            return Response(status=status.HTTP_200_OK)

        return Response(
            "Book is already returned", status.HTTP_406_NOT_ACCEPTABLE
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
