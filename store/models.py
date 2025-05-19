from typing import AnyStr, Dict, Callable, Tuple, Set
from copy import copy, deepcopy

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

	# updating in UserBookRelation.save()
	average_rating = models.FloatField(default = None, null = True)
	ratings_count = models.IntegerField(default = 0)
	likes_count  = models.IntegerField(default = 0)

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
	
	class Meta:
		unique_together = [
			['user', 'book']
		]

	def __str__(self) -> str:
		def prepare_string(text: AnyStr, max_length: int = 32):
			text: str = str(text)
			return (text[:max_length - 3].strip() + '...') if len(text) > max_length else text

		return str(f'Relation between "{prepare_string(self.user)}" and "{prepare_string(self.book, max_length = 48)}"')


	def save(self, *args, **kwargs):
		from . import logic

		is_creating = not self.pk

		old_relation = UserBookRelation.objects.get(book = self.book, user = self.user) if not is_creating else self

		super().save(*args, **kwargs)

		if  old_relation.rate != self.rate or is_creating:
			logic.calculate_and_update_book_average_rating(self.book)
			logic.calculate_and_update_book_ratings_count(self.book)

		if  old_relation.liked != self.liked or is_creating:
			logic.calculate_and_update_book_likes_count(self.book)


		# а вот надо было по тупому делать
		'''
		FIELD_NAMES_AND_ACTIONS_ON_CHANGE: Dict[str, Tuple[Callable[[Book], None]]] = {
			'rate': (
				logic.calculate_and_update_book_average_rating,
				logic.calculate_and_update_book_ratings_count,
			),
			'liked': (logic.calculate_and_update_book_likes_count,),
		}

		# а нужен ли тут copy()?
		# а copy() и не работает, ровно как и deepcopy()
		old_relation = copy(self)

		super().save(*args, **kwargs)

		for relation_field_name, \
			actions \
		in FIELD_NAMES_AND_ACTIONS_ON_CHANGE.items():
			# if getattr(old_relation, relation_field_name) \
			# == getattr(self,         relation_field_name):
			# 	continue

			for action in actions:
				action(self.book)
		'''
		