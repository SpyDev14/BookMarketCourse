from typing import AnyStr

from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models



class Book(models.Model):
	name = models.CharField(max_length = 255)
	price = models.DecimalField(max_digits = 8, decimal_places = 2, validators=[MinValueValidator(1)])
	author = models.CharField(max_length=255)
	description = models.TextField(max_length = 4096, blank = True)
	owner = models.ForeignKey(
		User,
		on_delete = models.SET_NULL,
		null = True,
		related_name = 'my_books'
	)

	readers = models.ManyToManyField(User, through = 'UserBookRelation', related_name = 'books')

	def __str__(self) -> str:
		return str(self.name)


class UserBookRelation(models.Model):
	RATE_CHOISES: tuple = (
		(0, 'Very bad'),
		(1, 'Bad'),
		(2, 'Not bad'),
		(3, 'Cool'),
		(4, 'Fine'),
		(5, 'Great'),
	)

	user = models.ForeignKey(User, on_delete = models.CASCADE)
	book = models.ForeignKey(Book, on_delete = models.CASCADE)
	rate = models.PositiveSmallIntegerField(choices = RATE_CHOISES, blank = True, null = True)
	liked = models.BooleanField(default = False)
	in_bookmarks = models.BooleanField(default = False)

	def __str__(self) -> str:
		def prepare_string(text: AnyStr, max_length: int = 32):
			text: str = str(text)
			return (text[:max_length - 3].strip() + '...') if len(text) > max_length else text

		return str(f'Relation between "{prepare_string(self.user)}" and "{prepare_string(self.book, max_length = 48)}"')