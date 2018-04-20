####-----------------------------Final Project Testing--------------------------

import unittest
from final_project import *

call_func = get_data()
class TestDataAccess(unittest.TestCase):
# Using The Dark Knight For Testing the Movie Dictionary
# Year = 2008 Length = 2h 32 min Genre = Action, Crime, Drama,
# Score = 9.0/10 Director = Christopher Nolan
# Lead Star = Christian Bale Supporting = Heath Ledger
# 82 Metascore
    def test_movie_dictionary(self):
        self.assertIn('The Dark Knight', movie_dict)
        self.assertEqual(movie_dict['The Dark Knight']['Genre'], 'Action, Crime, Thriller')
        self.assertEqual(movie_dict['The Dark Knight']['Year'], 2008)
        self.assertEqual(movie_dict['The Dark Knight']['Length'], '2h 32min')
        self.assertEqual(movie_dict['The Dark Knight']['Score out of 10'], 9.0)
        self.assertEqual(type(movie_dict['The Dark Knight']['Score out of 10']), float)
        self.assertEqual(movie_dict['The Dark Knight']['Director'], 'Christopher Nolan')
        self.assertEqual(movie_dict['The Dark Knight']['Rating'], 'Rated PG-13 for intense sequences of violence and some menace')
        self.assertEqual(movie_dict['La Haine']['Rating'], 'Not Rated')
        self.assertEqual(type(movie_dict['The Dark Knight']['Storyline']), str)
        self.assertEqual(movie_dict['The Dark Knight']['Main Actor/Actress'], 'Christian Bale')
        self.assertEqual(movie_dict['The Dark Knight']['Metascore'], 82)
# Using Steve McQueen for Testing the Director Dictionary, he directed 12 Years a Slave
    def test_director_dictionary(self):
        self.assertIn('Steve McQueen', director_dict)
        self.assertEqual(director_dict['Steve McQueen']['Birthplace'], 'London, England, UK')
        self.assertEqual(director_dict['Steve McQueen']['Awards'], 'Won 1 Oscar.')
        self.assertEqual(director_dict['David Lynch']['Awards'], 'Nominated for 4 Oscars.')
        self.assertEqual(director_dict['Mathieu Kassovitz']['Awards'], 'Director has not won or been nominated for any awards')
        self.assertEqual(director_dict['Steve McQueen']['First Movie Known For'], '12 Years a Slave')
        self.assertEqual(director_dict['Steve McQueen']['Second Movie Known For'], 'Shame')
        self.assertEqual(director_dict['Steve McQueen']['Third Movie Known For'], 'Hunger')
        self.assertEqual(director_dict['Steve McQueen']['Fourth Movie Known For'], 'Widows')
# Using Jodie Foster from Silence of the Lambs and Omar Sy from the Intouchables for Testing Actor Dictionary
    def test_actor_dictionary(self):
        self.assertIn('Jodie Foster', actor_dict)
        self.assertIn('Omar Sy', actor_dict)
        self.assertEqual(actor_dict['Jodie Foster']['Title'], 'Actress')
        self.assertEqual(actor_dict['Omar Sy']['Title'], 'Actor')
        self.assertEqual(actor_dict['Jodie Foster']['Awards'], 'Won 2 Oscars.')
        self.assertEqual(actor_dict['Omar Sy']['Awards'], 'Actor or Actress has not won or been nominated for any awards')
        self.assertEqual(actor_dict['Jodie Foster']['Awards'], 'Won 2 Oscars.')
        self.assertEqual(actor_dict['Jodie Foster']['First Media Known For'], 'The Silence of the Lambs')
        self.assertEqual(actor_dict['Jodie Foster']['Second Media Known For'], 'Contact')
        self.assertEqual(actor_dict['Jodie Foster']['Third Media Known For'], 'The Accused')
        self.assertEqual(actor_dict['Jodie Foster']['Fourth Media Known For'], 'Taxi Driver')
        self.assertEqual(actor_dict['Omar Sy']['First Media Known For'], 'The Intouchables')
        self.assertEqual(actor_dict['Omar Sy']['Second Media Known For'], 'Jurassic World')
        self.assertEqual(actor_dict['Omar Sy']['Third Media Known For'], 'X-Men: Days of Future Past')
        self.assertEqual(actor_dict['Omar Sy']['Fourth Media Known For'], 'Transformers: The Last Knight')

class TestStorage(unittest.TestCase):
    def test_movies_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = 'SELECT MovieName FROM Movies'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('The Departed',), result_list)
        self.assertEqual(len(result_list), 250)

        sql = '''
            SELECT MovieName, Genre, Year,
                   MovieScore, Rating, LeadName
            FROM Movies
            WHERE LeadName="Harrison Ford"
            ORDER BY MovieScore DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 4)
        self.assertEqual(result_list[0][3], 8.5)

        #-----Test Join--------------------------#
        statement = '''
        SELECT Movies.Director, Count(*)
        FROM Movies
	       JOIN Directors
           ON Movies.DirectorId = Directors.Id
        WHERE Directors.Birthplace LIKE '%London%'
        GROUP BY Movies.Director
        ORDER BY Count(*) DESC
        '''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Christopher Nolan', 7), result_list)
        self.assertEqual(len(result_list), 7)

        conn.close()

    def test_directors_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = 'SELECT DirectorName FROM Directors'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Martin Scorsese',), result_list)
        self.assertEqual(len(result_list), 151)

        sql = '''
        SELECT Count(*)
        FROM Directors
        WHERE Directors.Awards = 'Won 3 Oscars.'
        '''
        results = cur.execute(sql)
        count = cur.fetchall()[0]
        self.assertEqual(count[0], 6)

        conn.close()

    def test_actors_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = 'SELECT Name FROM Actors'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Tom Hanks',), result_list)
        self.assertEqual(len(result_list), 382)

        conn.close()


unittest.main(verbosity=2)
