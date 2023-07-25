from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    cover_choices = (("HARD", "hard cover"), ("SOFT", "soft cover"))

    cover = models.CharField(
        max_length=60, choices=cover_choices, default="SOFT"
    )

    def clean(self) -> None:
        if self.inventory < 0:
            raise ValidationError(
                f"Inventory should be a positive number, not {self.inventory}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title", "author"]

    def __str__(self) -> str:
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["borrow_date"]

    def __str__(self) -> str:
        return f"Book: {self.book.title}, return date: {self.expected_return_date}"
