from copy import copy

from django.contrib.auth.models import User
from django.test                import TestCase

from store.serializers import BookSerializer
from store.models      import Book, UserBookRelation
from store.logic       import *



class CalculateAndUpdateFunctionsTestCase(TestCase):
	def setUp(self):
		users_list = [
			User.objects.create(
				username = 'DebugUser1',
				password = 'DebugPass',
				first_name = 'Nikolae',
				last_name = 'Chaushesko'
			),

			User.objects.create(
				username = 'DebugUser2',
				password = 'DebugPass',
				first_name = 'Anton'
			),

			User.objects.create(
				username = 'DebugUser3',
				password = 'DebugPass',
			),

			User.objects.create(
				username = 'DebugUser4',
				password = 'DebugPass',
				last_name = 'Zubeknakov'
			),

			User.objects.create(
				username = 'DebugUser5',
				password = 'DebugPass',
				last_name = 'Chigur'
			),
		]
		self.users = User.objects.filter(
			pk__gte = users_list[0].pk,
			pk__lte = users_list[len(users_list)-1].pk
		).order_by('id')

		users = self.users
		books_list = [
			Book.objects.create(
				name = 'Сборник анегдотов за 2008 год',
				price = '250.00',
				author = 'Геннадий Горин',
				owner = users[0]
			),
			Book.objects.create(
				name = 'The legends of the Nar\'Cie',
				price = '1200.00',
				author = 'Space Station Lore-Master',
				description = '''
Welcome to the archive of N̗̲̬a̤̪̬̰r̻̹ͅ-S͉͍i̸͈͈̺e͚̮̹̖̮͍̩, intrepid reader,
Within you shall find all our knowlege about Ṇ͠a̭̮͠r͍̗̝͕̪ͅ-S̺̤̺̩͙͉̰i̞͙e̹̗͇̗̩͎͟ͅ .
It may only be summoned by nine powerful acolytes,
Chanting around an arcane rune of great power.
Those nine make a great sacrifice in calling It back,

F̱̫̝͟o̰̰r̟̙̲͇͘ ̻̩̫͝I̧͇͉t̘̹̯̙̤͖̳ s̬̠͙̘̕h̶̞̰̻al̞̮̮̯̩̼̺l̙̙͖͚̭̳ ̧̠̞͎͍c̴̼͖̻̖̪͕o̵n͏͙̲̪̺̗̫s̺̰̞̜úm̟e̛̟̭ ͈͍̪t̡h͈em̹̼͈͙ ̢̻̺̠̬̩̙u̯̞̼͇̞ͅṕ̩͕̜̣o̢̭͈͎̜͍̼ͅn͖ r̰̟̩̙͎i͔͟s͉̖̟i̼͚̱͖̪̙̤n͎̠͓͖ͅg̳̣͎͎ ̖͇̥̩̻̣̭̀f̦̟̝̮͢r͇͓ọ̠̭͎̮m҉ ̫t͔͍̟͉̗͉̳h̫͙e ͓͚v̲̬o̹̳͙id͈͍̟.
'''.strip(),
				owner = None
			)
		]
		self.books = Book.objects.filter(
			pk__gte = books_list[0].pk,
			pk__lte = books_list[len(books_list)-1].pk
		).order_by('id')

		books = self.books
		relations_list = [
			UserBookRelation.objects.create(
				user = users[0],
				book = books[0],

				liked = True,
				rate  = 1
			),
			
			UserBookRelation.objects.create(
				user = users[0],
				book = books[1],

				liked = True,
				rate  = 2
			),
			
			UserBookRelation.objects.create(
				user = users[1],
				book = books[0],

				liked = False,
				rate  = 0
			),
			
			UserBookRelation.objects.create(
				user = users[2],
				book = books[1],

				liked = True,
				rate  = 4
			),

			UserBookRelation.objects.create(
				user = users[3],
				book = books[0],

				liked = False,
			),
		]

		self.relations = UserBookRelation.objects.filter(
			pk__range = (
				relations_list[0].pk,
				relations_list[len(relations_list)-1].pk
			)
		).order_by('id')


	def test_all(self):
		book = self.books[0]

		def build_error_message(obd: dict, nbd: dict) -> str:
			return f'''
{' '*(16+1)            }|{f"{'Old':^9}"               }|{f"{'New':^9}"               }|
|:{'-'*(16-2)         }:|:{'-'*(9-2)                 }:|:{'-'*(9-2)                 }:|
|{' Average rating':<16}|{f'{obd["average_rating"]:.2f}' if obd['average_rating'] else 'null':^9}|{f'{nbd["average_rating"]:.2f}' if nbd['average_rating'] else 'null':^9}|
|{ ' Ratings count':<16}|{str(obd['ratings_count']):^9}|{str(nbd['ratings_count']):^9}|
|{   ' Likes count':<16}|{str(obd['likes_count']  ):^9}|{str(nbd['likes_count']  ):^9}|
'''

		old_book_data: dict = BookSerializer(book).data
		
		relation = UserBookRelation.objects.create(
			user = self.users[4],
			book = book,
			rate = 5, 
			liked = True
		)
		book.refresh_from_db()

		new_book_data: dict = BookSerializer(book).data
		self.assertNotEqual(new_book_data, old_book_data, build_error_message(old_book_data, new_book_data))


		old_book_data = BookSerializer(book).data

		relation.liked = False
		relation.save()
		book.refresh_from_db()

		new_book_data = BookSerializer(book).data
		self.assertNotEqual(new_book_data, old_book_data, build_error_message(new_book_data, old_book_data))


		old_book_data = BookSerializer(book).data

		relation.rate = 3
		relation.save()
		book.refresh_from_db()

		new_book_data = BookSerializer(book).data
		self.assertNotEqual(new_book_data, old_book_data, build_error_message(new_book_data, old_book_data))


		old_book_data = BookSerializer(book).data

		relation.rate = 5
		relation.liked = True
		relation.save()
		book.refresh_from_db()

		new_book_data = BookSerializer(book).data
		self.assertNotEqual(new_book_data, old_book_data, build_error_message(new_book_data, old_book_data))