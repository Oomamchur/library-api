from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )

    cover_choices = (("HARD", "hard cover"), ("SOFT", "soft cover"))

    cover = models.CharField(
        max_length=60, choices=cover_choices, default="SOFT"
    )

    class Meta:
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self) -> str:
        return (
            f"Book: {self.book.title}, "
            f"return date: {self.expected_return_date}"
        )
