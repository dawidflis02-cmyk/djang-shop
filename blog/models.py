from django.db import models


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Elektronika'),
        ('clothing', 'Odzież'),
        ('books', 'Książki'),
        ('food', 'Żywność'),
        ('other', 'Inne'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def short_description(self, word_limit: int = 30) -> str:
        words = self.description.split()
        if len(words) <= word_limit:
            return self.description
        return " ".join(words[:word_limit]) + "..."
