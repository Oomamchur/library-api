from django.contrib import admin

from library.models import Book, Borrowing

admin.site.register(Book)
admin.site.register(Borrowing)
