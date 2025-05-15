from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . import models

@admin.register(models.Book)
class BookAdmin(ModelAdmin): ...

@admin.register(models.UserBookRelation)
class UserBookRelationAdmin(ModelAdmin): ...