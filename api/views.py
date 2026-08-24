from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from zevera.models import Category
from .serializers import CategorySerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Create your views here.
