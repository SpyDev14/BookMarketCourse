from typing import Dict, Any, List
import copy

from django.db.models.functions.math import Round
from django.db.models.manager        import BaseManager
from django.db.models                import Avg, Count, Q
from django.db                       import connection
from django.test.utils               import CaptureQueriesContext
from django.contrib.auth.models      import User
from django.urls                     import reverse
from django.http                     import HttpResponse
from rest_framework.test             import APITestCase
from rest_framework                  import status

from store.serializers import BookSerializer
from store.models      import *


# Used in setUp
from store.views import BooksViewSet
BOOK_QUERYSET = BooksViewSet.queryset
del BooksViewSet

# used in test_get & test_get_detail
NORMAL_COUNT_OF_BOOK_DATABASE_QUERIES: int = 2


# MARK: Books
class BooksApiTestCase(APITestCase):
	def setUp(self):
		self.user = User.objects.create(
			username = 'DebugUser',
			password = 'very_hard_pass',
		)

		# просто для первого теста, потом оно удаляется в нём же
		self.user_own_books_list: List[Book] = [
			Book.objects.create(
				name = 'Как правильно составлять дизайн-документ',
				price = '375.00',
				author = 'GaDever',
				owner = self.user
			),

			Book.objects.create(
				name = 'Beholder - сюжет и сеттинг',
				price = '375.00',
				author = 'mr.Observer',
				owner = self.user
			) 
		]
		self.user_not_own_books_list: List[Book] = [
			Book.objects.create(
				name = 'Сборник анегдотов за 2008 год',
				price = '250.00',
				author = 'Геннадий Павлович'
			),

			Book.objects.create(
				name = 'The legends of the Nar\'Cie',
				price = '1200.00',
				author = 'Space Station Lore-master'
			),

			Book.objects.create(
				name = "Scrap Guideliner - who is it?",
				price = "1200.00",
				author = "Anonimous"
			),

			Book.objects.create(
				name = "Scrap Mechanic - a guide for dummies",
				price = "320.00",
				author = "PosX"
			),

			Book.objects.create(
				name = "Tanks and guns in Scrap Mechanic - a guide for dummies",
				price = "375.00",
				author = "Scrap Guideliner"
			),

			Book.objects.create(
				name = "Scrap Mechanic Modding Guideline in 2025",
				price = "450.00",
				author = "Scrap Guideliner"
			),
		]


		self.user_own_books = BOOK_QUERYSET.filter(
			pk__range = (
				self.user_own_books_list[0].pk,
				self.user_own_books_list[len(self.user_own_books_list)-1].pk
			)
		)

		self.user_not_own_books = BOOK_QUERYSET.filter(
			pk__range = (
				self.user_not_own_books_list[0].pk,
				self.user_not_own_books_list[len(self.user_not_own_books_list)-1].pk
			)
		)

		self.books = BOOK_QUERYSET.filter(
			pk__range = (
				self.user_own_books[0].pk,
				self.user_not_own_books[len(self.user_not_own_books)-1].pk
			)
		)

	def test_setUp_books_iterables(self):
		books = self.user_own_books_list + self.user_not_own_books_list

		for i in range(0, len(self.books)-1):
			self.assertEqual(books[i], self.books[i])

		for i in range(0, len(self.user_own_books)-1):
			self.assertEqual(self.user_own_books[i], self.user_own_books[i])

		for i in range(0, len(self.user_not_own_books)-1):
			self.assertEqual(self.user_not_own_books[i], self.user_not_own_books[i])

		del self.user_own_books_list
		del self.user_not_own_books_list


	def test_get(self):
		url = reverse('book-list')

		responce = None
		with CaptureQueriesContext(connection) as queries:
			responce = self.client.get(url)

			self.assertEqual(len(queries), NORMAL_COUNT_OF_BOOK_DATABASE_QUERIES)
		
		self.assertEqual(status.HTTP_200_OK, responce.status_code)
		self.assertEqual(BookSerializer(self.books, many = True).data, responce.data)


	def test_get_detail(self):
		book = self.books[0]
		url = reverse('book-detail', args = (book.pk, ))

		responce = None
		with CaptureQueriesContext(connection) as queries:
			responce = self.client.get(url)
			self.assertEqual(len(queries), NORMAL_COUNT_OF_BOOK_DATABASE_QUERIES)
		
		self.assertEqual(status.HTTP_200_OK, responce.status_code)
		self.assertEqual(BookSerializer(book).data, responce.data)

	
	def test_get_filtered_and_ordered(self):
		url = reverse('book-list')
		responce = self.client.get(url, data = {'search': 'Scrap', 'ordering': 'author,-price'})
		books = self.books
		expected_data = BookSerializer([books[4], books[5], books[7], books[6]], many = True).data

		import json
		self.assertEqual(status.HTTP_200_OK, responce.status_code)
		self.assertEqual(expected_data, responce.data, msg = f"""
\033[1;31mDATA:\033[0m
{json.dumps(responce.data, indent=4, ensure_ascii=False)}

\033[1;35mEXPECTED DATA:\033[0m
{json.dumps(expected_data, indent=4, ensure_ascii=False)}

\033[2mps: порядок не важен\033[0m
""" .replace('"', '\033[1;33m"')
	.replace('\033[1;33m":', '"\033[0m:')
	.replace('\033[1;33m",', '"\033[0m,')
	.replace('"', '\'')
)

	def test_create(self):
		url = reverse('book-list')

		books_count: int = Book.objects.all().count()


		data = {
			'name': 'Debug Book',
			'price': '333',
			'author': 'Entity413',
			'owner': 1
		}

		responce = self.client.post(url, data = data)
		self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(books_count, Book.objects.all().count())

		self.client.force_login(self.user)

		responce = self.client.post(url, data = data, content_type='application/json')
		self.assertEqual(responce.status_code, status.HTTP_201_CREATED)
		self.assertEqual(books_count + 1, Book.objects.all().count())
		self.assertEqual(self.user.username, Book.objects.last().owner.username)

	
	def test_update(self):
		url = reverse('book-detail', args = (self.user_not_own_books[0].pk, ))

		responce = self.client.get(url)
		self.assertEqual(responce.status_code, status.HTTP_200_OK)
		
		responce = self.client.patch(url, data = { 'price': str(840) }, content_type='application/json')
		self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)


		self.client.force_login(self.user)
		
		responce = self.client.get(url)
		self.assertEqual(responce.status_code, status.HTTP_200_OK)

		responce = self.client.patch(url, data = { 'price': str(840) }, content_type='application/json')
		self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)

		for book in self.user_own_books:
			url = reverse('book-detail', args = (book.pk, ))
			old_price = book.price

			for i in range(-1, 0):
				responce = self.client.patch(url, data = { 'price': str(i) }, content_type='application/json')

				wrong_price_expected_body = {
					"price": [
						"Ensure this value is greater than or equal to 1."
					]
				}
				
				book.refresh_from_db()

				self.assertEqual(responce.status_code, status.HTTP_400_BAD_REQUEST)
				self.assertEqual(responce.json(),      wrong_price_expected_body)
				self.assertEqual(
					str(old_price),
					str(Book.objects.get(pk = book.pk).price)
				)

			for i in [1_000_000_000, 100_000_000]:
				responce = self.client.patch(url, data = { 'price': str(i) }, content_type='application/json')

				wrong_price_expected_body = {
					"price": [
						"Ensure that there are no more than 8 digits in total."
					]
				}


				self.assertEqual(responce.status_code, status.HTTP_400_BAD_REQUEST)
				self.assertEqual(responce.json(),      wrong_price_expected_body)
				self.assertEqual(
					str(old_price),
					str(Book.objects.get(pk = book.pk).price)
				)

			for i in [10_000_000, 1_000_000]:
				responce = self.client.patch(url, data = { 'price': str(10_000_000) }, content_type='application/json')

				wrong_price_expected_body = {
					"price": [
						"Ensure that there are no more than 6 digits before the decimal point."
					]
				}

				self.assertEqual(responce.status_code, status.HTTP_400_BAD_REQUEST)
				self.assertEqual(responce.json(),      wrong_price_expected_body)
				self.assertEqual(
					str(old_price),
					str(Book.objects.get(pk = book.pk).price)
				)


			responce = self.client.patch(url, data = { 'price': str(250) }, content_type = 'application/json')
			book.refresh_from_db()
			self.assertEqual(responce.status_code, status.HTTP_200_OK)
			self.assertEqual(str(book.price), '250.00')
			self.assertEqual(str(book.price), str(Book.objects.get(pk = book.pk).price))


	def test_delete(self):
		self.client.force_login(self.user)
		book_for_delete = Book.objects.create(
			name = 'Book for delete',
			price = '127.00',
			author = 'Debugger',
			owner = self.user
		)
		book_count = Book.objects.all().count()
		url = reverse('book-detail', args = (book_for_delete.pk, ))
		responce = self.client.delete(url)
		
		self.assertEqual(responce.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(book_count - 1, Book.objects.all().count())



# MARK: User Book Relation
# MARK: BUG!!!
# Можно создать несколько отношений между одним и тем же пользователем и книгой !!!
class UserBookRelationApiTestCase(APITestCase):
	def setUp(self):
		self.user1 = User.objects.create(
			username = 'DebugUser1',
			password = 'very_hard_pass',
		)

		self.user2 = User.objects.create(
			username = 'DebugUser2',
			password = 'very_hard_pass',
		)

		self.user1_own_books_list: List[Book] = [
			Book.objects.create(
				name = 'Как правильно составлять дизайн-документ',
				price = '375.00',
				author = 'GaDever',
				owner = self.user1
			),

			Book.objects.create(
				name = 'Beholder - сюжет и сеттинг',
				price = '375.00',
				author = 'mr.Observer',
				owner = self.user1
			),

			Book.objects.create(
				name = 'Сборник анегдотов за 2008 год',
				price = '250.00',
				author = 'Геннадий Павлович',
				owner = self.user1
			),

			Book.objects.create(
				name = 'The legends of the Nar\'Cie',
				price = '1200.00',
				author = 'Space Station Lore-master',
				owner = self.user1
			),
		]

		self.user2_own_books_list: List[Book] = [
			Book.objects.create(
				name = "Scrap Guideliner - who is it?",
				price = "1200.00",
				author = "Anonimous",
				owner = self.user2
			),

			Book.objects.create(
				name = "Scrap Mechanic - a guide for dummies",
				price = "320.00",
				author = "PosX",
				owner = self.user2
			),

			Book.objects.create(
				name = "Tanks and guns in Scrap Mechanic - a guide for dummies",
				price = "375.00",
				author = "Scrap Guideliner",
				owner = self.user2
			),

			Book.objects.create(
				name = "Scrap Mechanic Modding Guideline in 2025",
				price = "450.00",
				author = "Scrap Guideliner",
				owner = self.user2
			),
		]

		self.user1_own_books = Book.objects.filter(owner = self.user1)
		self.user2_own_books = Book.objects.filter(owner = self.user2)

		self.books: List[Book] = Book.objects.filter(owner__in=[self.user1, self.user2])


	def test_setUp_books_iterables(self):
		books = self.user1_own_books_list + self.user2_own_books_list

		for i in range(0, len(self.books)-1):
			self.assertEqual(books[i], self.books[i])

		for i in range(0, len(self.user1_own_books)-1):
			self.assertEqual(self.user1_own_books[i], self.user1_own_books[i])

		for i in range(0, len(self.user2_own_books)-1):
			self.assertEqual(self.user2_own_books[i], self.user2_own_books[i])

		del self.user1_own_books_list
		del self.user2_own_books_list


	def test_get(self):
		book = self.user2_own_books[0]
		url = reverse('bookrelations-detail', args = (book.pk,))

		self.client.force_login(self.user1)

		responce = self.client.patch(url, data = { 'liked' : True }, content_type='application/json')
		relation = UserBookRelation.objects.get(user = self.user1, book = book)
		
		self.assertEqual(responce.status_code, status.HTTP_200_OK)
		self.assertTrue(relation.liked)

		responce = self.client.patch(url, data = { 'liked' : False }, content_type='application/json')
		relation.refresh_from_db()
		self.assertEqual(responce.status_code, status.HTTP_200_OK)
		self.assertFalse(relation.liked)


		responce = self.client.patch(url, data = { 'rate': 3, 'liked' : False }, content_type='application/json')
		relation.refresh_from_db()
		self.assertEqual(responce.status_code, status.HTTP_200_OK)
		self.assertEqual(relation.rate, 3)
		self.assertFalse(relation.liked)


		responce = self.client.patch(url, data = { 'rate': 5, 'liked' : True }, content_type='application/json')
		relation.refresh_from_db()
		self.assertEqual(responce.status_code, status.HTTP_200_OK)
		self.assertEqual(relation.rate, 5)
		self.assertTrue(relation.liked)
	
	def test_try_create_duplicate(self):
		pass