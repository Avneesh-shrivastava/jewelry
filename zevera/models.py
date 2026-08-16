from django.db import models

# Create your models here.
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    css_class = models.CharField(
        max_length=50, blank=True,
        help_text="Fallback gradient class if no image, e.g. cat-rings"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    prod_desc = models.TextField(max_length=500)
    image = models.ImageField(upload_to='product_img/', blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
   
    def __str__(self):
        return self.name

class extra_info(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='extra_info',null=True)
    headline = models.CharField(max_length=200)
    headline_desc = models.CharField(max_length=300)

class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews',null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField(max_length=500)
    stars = models.IntegerField(null=True)
    # review_score = models.IntegerField(null=True)

class Cart(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart',null=True)
    quantity = models.IntegerField()
    product = models.CharField(max_length=100)
    price = models.FloatField()
    size = models.CharField(max_length=5, null=True)
