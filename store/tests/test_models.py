from django.contrib.auth.models import User
from django.test                import TestCase
from django.db.utils            import IntegrityError

from store.models import Book, UserBookRelation


class UserBookRelationTestCase(TestCase):
	def setUp(self):
		users_list = [
			User.objects.create(
				username = 'DebugUser1',
				password = 'VeryHardPass'
			),

			User.objects.create(
				username = 'DebugUser2',
				password = 'VeryHardPass'
			)
		]
		books_list = [
			Book.objects.create(
				name = 'Сборник анегдотов за 2008 год',
				price = '250.00',
				author = 'Геннадий Горин'
			),
			Book.objects.create(
				name = 'The legends of the Nar\'Cie',
				price = '1200.00',
				author = 'Space Station Lore-Master'
			)
		]
		relations_list = [
			UserBookRelation.objects.create(
				user = users_list[0],
				book = books_list[1],
				# rate = ...,
				liked = True
			),

			UserBookRelation.objects.create(
				user = users_list[1],
				book = books_list[0],
				rate = 3,
				# liked = ...,
			),

			UserBookRelation.objects.create(
				user = users_list[1],
				book = books_list[1],
				liked = True,
				rate = 5
			),
		]


		self.users = User.objects.filter(
			pk__range = (
				users_list[0].pk,
				users_list[len(users_list)-1].pk
			)
		)

		self.books = Book.objects.filter(
			pk__range = (
				books_list[0].pk,
				books_list[len(books_list)-1].pk
			)
		)

		self.relations = UserBookRelation.objects.filter(
			pk__range = (
				relations_list[0].pk,
				relations_list[len(relations_list)-1].pk
			)
		)

	
	def test_create_none_unique_relation(self):
		old_last = UserBookRelation.objects.last()

		# Такой связи нет
		UserBookRelation.objects.create(
			user = self.users[0],
			book = self.books[0],
			rate = 5,
			liked = True,
		)

		new_last = UserBookRelation.objects.last()
		self.assertNotEqual(new_last.pk, old_last.pk)


		ex: Exception | None = None
		# Такая связь есть
		try: 
			UserBookRelation.objects.create(
				user = self.users[1],
				book = self.books[1],
				rate = 5,
				liked = True,
			)
		except Exception as e:
			ex = e

		self.assertTrue(isinstance(ex, IntegrityError))