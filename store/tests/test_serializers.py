from django.db.models.functions.math import Round
from django.contrib.auth.models      import User
from django.db.models                import Avg, Count, Q
from django.test                     import TestCase

from store.serializers import *
from store.models      import Book

class BookSerializerTestCase(TestCase):
	def test_books(self):
		users: list[User] = [
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
		]

		books: list[Book] = [
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

		relations: list[UserBookRelation] = [
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
				user = users[2],
				book = books[1],

				liked = False,
				rate  = 5
			),

			UserBookRelation.objects.create(
				user = users[3],
				book = books[0],

				liked = False,
			),
		]

		annotated_books_qs = Book.objects.annotate(
			likes_count    = Count('userbookrelation', filter = Q(userbookrelation__liked = True)),
			ratings_count  = Count('userbookrelation', filter = Q(userbookrelation__rate__isnull = False)),
			average_rating = Round(
				Avg(
					'userbookrelation__rate',
					filter = Q(userbookrelation__rate__isnull = False )
				),
				precision = 2
			)
		).order_by('id')


		data = BookSerializer(annotated_books_qs, many = True).data

		expected_data = [
			{
				'id' : books[0].pk,
				'name': books[0].name,
				'price': books[0].price,
				'author': books[0].author,
				'description': books[0].description,
				'likes_count': 1,
				'ratings_count' : 2,
				'average_rating' : 0.5,
				'owner': {
					'username': users[0].username,
					'email': users[0].email,
				},
				'readers': [
					{
						'username': users[0].username,
						'first_name': users[0].first_name,
						'last_name': users[0].last_name,
					},
					{
						'username': users[1].username,
						'first_name': users[1].first_name,
						'last_name': users[1].last_name,
					},
					{
						'username': users[3].username,
						'first_name': users[3].first_name,
						'last_name': users[3].last_name,
					}
				],
			},
			{
				'id' : books[1].pk,
				'name': books[1].name,
				'price': books[1].price,
				'author': books[1].author,
				'description': books[1].description,
				'likes_count': 2,
				'ratings_count' : 3,
				'average_rating' : 3.67,
				'owner': None,
				'readers': [
					{
						'username': users[0].username,
						'first_name': users[0].first_name,
						'last_name': users[0].last_name,
					},
					{
						'username': users[2].username,
						'first_name': users[2].first_name,
						'last_name': users[2].last_name,
					},
					{
						'username': users[2].username,
						'first_name': users[2].first_name,
						'last_name': users[2].last_name,
					}
				],
			},
		]

		import json
		
		self.assertEqual(
			data,
			expected_data,
			f'''
\033[1;31mDATA:\033[0m
{json.dumps(data, indent = 4, ensure_ascii=False)}

\033[1;35mEXPECTED DATA:\033[0m
{json.dumps(expected_data, indent = 4, ensure_ascii=False)}

\033[2mps: порядок не важен\033[0m
'''	.replace('"', '\033[1;33m"')
	.replace('\033[1;33m":', '"\033[0m:')
	.replace('\033[1;33m",', '"\033[0m,')
	.replace('"\n', '"\033[0m\n')
	.replace('"', '\'')
)