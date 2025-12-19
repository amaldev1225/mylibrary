from django.db import models
from datetime import date, timedelta
import random

def generate_card_number():
    while True:
        num = str(random.randint(100000, 999999))
        if not Profile.objects.filter(card_number=num).exists():
            return num
class Profile(models.Model):
    full_name = models.CharField(max_length=150)
    card_number = models.CharField(max_length=10, unique=True, default=generate_card_number)

    def __str__(self):
        return f"{self.full_name} ({self.card_number})"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    quantity = models.IntegerField(default=1)     # total copies
    available = models.IntegerField(default=1)    # available copies

    def __str__(self):
        return self.title

    @property
    def issued_count(self):
        return Issue.objects.filter(book=self, returned=False).count()

class Issue(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    return_date = models.DateField(blank=True, null=True)
    returned = models.BooleanField(default=False)

    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.issue_date:
            self.issue_date = date.today()
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)

        super().save(*args, **kwargs)

    @property
    def current_fine(self):
        if self.returned:
            return self.fine_amount

        today = date.today()
        overdue = (today - self.due_date).days

        return overdue * 5 if overdue > 0 else 0

    def __str__(self):
        return f"{self.profile.full_name} → {self.book.title}"
