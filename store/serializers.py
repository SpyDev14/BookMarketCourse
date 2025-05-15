from django.contrib.auth.models import User
from rest_framework             import serializers

from .models import Book, UserBookRelation


class BookOwnerSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('username', 'email')

class BookReadersSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = (
			'username',
			'first_name',
			'last_name',
		)

class BookSerializer(serializers.ModelSerializer):
	# likes_count = SerializerMethodField()
	# average_rating = SerializerMethodField()

	likes_count    = serializers.IntegerField(read_only = True)
	ratings_count  = serializers.IntegerField(read_only = True)
	average_rating =   serializers.FloatField(read_only = True)

	# owner_name = serializers.CharField(source = 'owner.username', read_only = True, default = None)
	owner = BookOwnerSerializer(read_only = True)
	readers = BookReadersSerializer(many = True, read_only = True)

	class Meta:
		model = Book
		fields = (
			'id',
			'name',
			'price',
			'author',
			'description',
			'likes_count',
			'ratings_count',
			'average_rating',

			# 'owner_name',
			'owner',
			'readers',
		)
"""
	# сделал рейтинг ещё до того, как его сделали в видео
	# двумя вариантами, а это всё на память оставил, вдруг
	# надо будет, тут посмотрю, память освежу

	def get_likes_count(self, instance):
		return UserBookRelation.objects.filter(
			book = instance,
			liked = True
		).count()
	

	# выглядит как какое-то непотребство
	def get_average_rating(self, instance):
		ROUND_STEP: int = 2
		import statistics

		ratings = (
			UserBookRelation.objects
				.filter(book = instance)
				.exclude(rate = None)

				.values_list('rate', flat=True)
		)

		if not ratings:
			return None
		
		return round(
			statistics.mean(
				UserBookRelation.objects
					.filter(book = instance)
					.exclude(rate = None)

					.values_list('rate', flat=True)
			),

			ndigits = ROUND_STEP
		)
"""


class UserBookRelationSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserBookRelation
		fields = (
			'book',
			'liked',
			'rate',
			'in_bookmarks',
		)

		read_only_fields = (
			'book',
		)

		