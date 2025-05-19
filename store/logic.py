from django.db.models.functions.math import Round
from django.db.models import Avg, Q, Count

from .models import Book, UserBookRelation


def calculate_and_update_book_average_rating(book: Book) -> None:
	new_average_rating: float | None = (
		UserBookRelation.objects
		.filter(book = book)
		.aggregate(
			average_rating = Round(
				Avg('rate', filter = Q(rate__isnull = False)),
				precision = 2
			)
		).get('average_rating')
	)

# 	print(f'''
# |{"{:^8}".format('Old')}|{"{:^8}".format('New')}|
# |:{'-'*6}:|:{'-'*6}:|
# |{"{:^8}".format(book.average_rating or 'null')}|{"{:^8}".format(new_average_rating)}|
# ''')

	book.average_rating = new_average_rating
	book.save()


def calculate_and_update_book_ratings_count(book: Book) -> None:
	new_ratings_count: float | None = (
		UserBookRelation.objects
		.filter(book = book)
		.aggregate(ratings_count = Count('rate', filter = Q(rate__isnull = False)))
		.get('ratings_count')
	)

	book.ratings_count = new_ratings_count
	book.save()


def calculate_and_update_book_likes_count(book: Book) -> None:
	new_likes_count: float | None = (
		UserBookRelation.objects
		.filter(book = book)
		.aggregate(likes_count = Count('liked', filter = Q(liked = True)))
		.get('likes_count')
	)

	book.likes_count = new_likes_count
	book.save()