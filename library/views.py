from rest_framework import viewsets

from library.models import Book
from library.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = ()
