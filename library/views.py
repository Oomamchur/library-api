from rest_framework import viewsets

from library.models import Book
from library.serializers import BookSerializer, BookListSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = ()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
