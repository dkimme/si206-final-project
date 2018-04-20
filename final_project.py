##### Final Project: IMDB #####
import sqlite3
import json
import requests
import sys
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go

#-------------------------------------------------------------------------------
# Caching

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}


def get_unique_key(url):
    return url



def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


#-------------------------------------------------------------------------------
# Getting Data from IMDB
#-------------------------------------------------------------------------------
# Scrape IMDB homepage to get link for list of top 250 movies
url = 'http://www.imdb.com'
page_text = make_request_using_cache(url)
page_soup = BeautifulSoup(page_text, 'html.parser')
# print(page_soup.prettify())

content_div = page_soup.find_all('ul', class_='unstyled')
get_links = content_div[0].find_all('li')
crawl_url = ''
for x in get_links:
    if x.text.strip() == 'Top Rated Movies':
        crawl_url += x.find('a')['href']
top_movies_url = url + crawl_url
#-------------------------------------------------------------------------------
# scrape page with list of movies to access each movie individually
scrape_movies_lst = make_request_using_cache(top_movies_url)
soup_scrape = BeautifulSoup(scrape_movies_lst, 'html.parser')
# print(soup_scrape.text.strip())
content_div = soup_scrape.find('tbody', class_='lister-list')
table_rows = content_div.find_all('tr')
#-------------------------------------------------------------------------------
# Main Function
movie_dict = {}
director_dict = {}
actor_dict = {}
def get_data():
    # movie_listings = []
    # director_listings = []
    # actor_listings = []
    for tr in table_rows:
        table_data = tr.find('td', class_='titleColumn')
        # print(table_data)

        #------------------------------------------------------------
        # got the titles of the movies and the years they came out
        find_a = table_data.find('a')
        movie_title = find_a.string
        # print(movie_title)
        find_span = table_data.find('span', class_="secondaryInfo")
        movie_year_parenthesis = find_span.string
        movie_year = int(movie_year_parenthesis[1:5])
        #------------------------------------------------------------
        # got the individual urls for each movie so that the code can
        # get all the information for each movie
        specific_movie_url = table_data.find('a')['href']
        # print(specific_movie_url)
        # print('-'*20)

        # scraping each movie page
        movie_information = url + specific_movie_url
        # print(movie_information)
        # print('-'*20)
        scrape_movie_page = make_request_using_cache(movie_information)
        soup_page = BeautifulSoup(scrape_movie_page, 'html.parser')
        # print(soup_page.text.strip())

        #------------------------------------------------------------
        # get movie socres by IMDB users
        movie_score_info = soup_page.find('div', class_='ratingValue')
        movie_score_tag = movie_score_info.find('span', itemprop="ratingValue")
        movie_score_string = movie_score_tag.string.strip()
        movie_score = float(movie_score_string)

        #------------------------------------------------------------
        # get length, genre
        movie_other_info = soup_page.find('div', class_='subtext')

        time_tag = movie_other_info.find('time')
        movie_length = time_tag.text.strip()
        genre_tag = movie_other_info.find_all('span', class_="itemprop", itemprop="genre")
        if len(genre_tag) == 2:
            movie_genre = genre_tag[0].string.strip() + ", " + genre_tag[1].string.strip()
        elif len(genre_tag) == 3:
            movie_genre = genre_tag[0].string.strip() + ", " + genre_tag[1].string.strip() + ", " + genre_tag[2].string.strip()
        else:
            movie_genre = genre_tag[0].string.strip()

        # #------------------------------------------------------------
        # get director name and get url for diretors page
        find_director_span = soup_page.find('span', itemprop="director")
        find_director_div = find_director_span.find('span', class_="itemprop", itemprop="name")
        movie_director = find_director_div.text.strip()

        director_url = find_director_span.find('a')['href']
        crawl_director_url = url + director_url

        scrape_director_page = make_request_using_cache(crawl_director_url)
        director_soup = BeautifulSoup(scrape_director_page, 'html.parser')

        director_name_span = director_soup.find('span', class_="itemprop", itemprop="name")
        director_name = director_name_span.string.strip()


        #-----------director info--------------------

        director_info_div = director_soup.find('div', id="name-born-info", class_="txt-block")
        try:
            birthplace_find_a = director_info_div.find_all('a')
            director_birthplace = birthplace_find_a[-1].string.strip()
        except:
            director_birthplace = ''
        # if not none

        try:
            award_span = director_soup.find_all('span', itemprop="awards")
            award_b = award_span[0].find('b')
            director_oscars_newline = award_b.text.replace("\n", " ").strip()
            director_oscars = director_oscars_newline.replace("         ", " ")
        except:
            director_oscars = "Director has not won or been nominated for any awards"

        director_known_for_div = director_soup.find_all('div', class_="knownfor-title-role")
        known_for = []
        for movies in director_known_for_div:
            known_for_a = movies.find('a')
            known_for.append(known_for_a.text.strip())


        #------------------------------------------------------------
        # get movie rating ["G", "PG", "PG-13", "R", "NC-17", "Not rated", "Approved"]
        try:
            rating_info = soup_page.find('span', itemprop="contentRating")
            movie_rating = rating_info.string.strip()
        except:
            movie_rating = "rating not listed"

        #------------------------------------------------------------
        # get star actors/actresses for each movie
        stars_find_span = soup_page.find_all('span', itemprop="actors")
        first_person = stars_find_span[0].find('span', class_="itemprop")
        primary_star = first_person.string.strip()
        second_person = stars_find_span[1].find('span', class_="itemprop")
        secondary_star = second_person.string.strip()

        #------------------------------------------------------------
        #---------------Primary Star Information---------------------
        primary_star_url = stars_find_span[0].find('a')['href']
        crawl_primary_star_url = url + primary_star_url
        scrape_primary_star_page = make_request_using_cache(crawl_primary_star_url)
        primary_star_soup = BeautifulSoup(scrape_primary_star_page, 'html.parser')

        primary_name_span = primary_star_soup.find('span', class_="itemprop", itemprop="name")
        primary_star_name = primary_name_span.string.strip()

        primary_job_title = primary_star_soup.find_all('span', class_="itemprop", itemprop="jobTitle")
        primary_actor_actress_first = primary_job_title[0].text.strip()
        try:
            primary_actor_actress_second = primary_job_title[1].text.strip()
        except:
            pass

        if primary_actor_actress_first == 'Actor' or primary_actor_actress_first == 'Actress':
            primary_star_actor_actress = primary_job_title[0].text.strip()
        elif primary_actor_actress_second == 'Actor' or primary_actor_actress_second == 'Actress':
            primary_star_actor_actress = primary_job_title[1].text.strip()
        else:
            primary_star_actor_actress = primary_job_title[2].text.strip()

        try:
            primary_award_span = primary_star_soup.find_all('span', itemprop="awards")
            primary_award_b = primary_award_span[0].find('b')
            primary_oscars_newline = primary_award_b.text.replace("\n", " ").strip()
            primary_oscars = primary_oscars_newline.replace("         ", " ")
        except:
            primary_oscars = "Actor or Actress has not won or been nominated for any awards"

        primary_known_for_div = primary_star_soup.find_all('div', class_="knownfor-title-role")
        primary_known_for = []
        for movies in primary_known_for_div:
            primary_known_for_a = movies.find('a')
            primary_known_for.append(primary_known_for_a.text)



        #--------------------------------------------------------------
        #---------------Secondary Star Information---------------------
        secondary_star_url = stars_find_span[1].find('a')['href']
        crawl_secondary_star_url = url + secondary_star_url
        scrape_secondary_star_page = make_request_using_cache(crawl_secondary_star_url)
        secondary_star_soup = BeautifulSoup(scrape_secondary_star_page, 'html.parser')

        secondary_name_span = secondary_star_soup.find('span', class_="itemprop", itemprop="name")
        secondary_star_name = secondary_name_span.string.strip()

        secondary_job_title = secondary_star_soup.find_all('span', class_="itemprop", itemprop="jobTitle")
        secondary_actor_actress_first = secondary_job_title[0].text.strip()
        try:
            secondary_actor_actress_second = secondary_job_title[1].text.strip()
        except:
            pass

        if secondary_actor_actress_first == 'Actor' or secondary_actor_actress_first == 'Actress':
            secondary_star_actor_actress = secondary_job_title[0].text.strip()
        elif secondary_actor_actress_second == 'Actor' or secondary_actor_actress_second == 'Actress':
            secondary_star_actor_actress = secondary_job_title[1].text.strip()
        else:
            secondary_star_actor_actress = secondary_job_title[2].text.strip()

        try:
            secondary_award_span = secondary_star_soup.find_all('span', itemprop="awards")
            secondary_award_b = secondary_award_span[0].find('b')
            secondary_oscars_newline = secondary_award_b.text.replace("\n", " ").strip()
            secondary_oscars = secondary_oscars_newline.replace("         ", " ")
        except:
            secondary_oscars = "Actor or Actress has not won or been nominated for any awards"

        secondary_known_for_div = secondary_star_soup.find_all('div', class_="knownfor-title-role")
        secondary_known_for = []
        for movies in secondary_known_for_div:
            secondary_known_for_a = movies.find('a')
            secondary_known_for.append(secondary_known_for_a.text)


        #------------------------------------------------------------
        # get metascore rating
        try:
            metascore_div = soup_page.find('div', class_ = "metacriticScore score_favorable titleReviewBarSubItem")
            metascore_span = metascore_div.find('span')
            metascore_rating = int(metascore_span.string)
        except:
            metascore_rating = 0

        #------------------------------------------------------------
        # get storyline
        storyline_div = soup_page.find('div', class_="inline canwrap", itemprop="description")
        find_paragraph = storyline_div.find('p')
        movie_storyline_strip = find_paragraph.text.strip(' \n')
        movie_storyline_replace = movie_storyline_strip.replace("\n", " ")
        movie_storyline = movie_storyline_replace.replace("                ", " ")


        #------------------------------------------------------------
        # get USA gross earnings from movie
        gross_earnings_div = soup_page.find_all('div', class_="txt-block")
        USA_gross_earnings = []
        for earnings in gross_earnings_div:
            try:
                gross_earnings_h4 = earnings.find('h4', class_="inline")
                if 'Gross USA:' in gross_earnings_h4.string.strip():
                    USA_gross_earnings.append(earnings.text.strip())
            except:
                pass
        if USA_gross_earnings == []:
            USA_gross_earnings.append("USA unknown")
        final_USA_gross_earnings = ''
        for x in USA_gross_earnings:
            final_USA_gross_earnings += x[12:]
        # month_lst = ['January', 'February', 'March', 'April',
        # 'May', 'June', 'July', 'August', 'September',
        # 'October', 'November', 'December']
        # if final_USA_gross_earnings in month_lst:
        #     print(final_USA_gross_earnings)
            # find_r = final_USA_gross_earnings.rfind(',')
        #     final_USA_gross_earnings = final_USA_gross_earnings[:find_r]
        # print(final_USA_gross_earnings)

        # putting it all into a dictionaries for the tables

        #---------------Movie Dictionary-------------------------------
        movie_dict[movie_title]={}
        # print(movie_dict)
        movie_dict[movie_title]['Genre'] = movie_genre
        movie_dict[movie_title]['Year'] = movie_year
        movie_dict[movie_title]['Storyline'] = movie_storyline.strip(' \n')
        movie_dict[movie_title]['Score out of 10'] = movie_score
        movie_dict[movie_title]['Length'] = movie_length
        movie_dict[movie_title]['Director'] = movie_director
        movie_dict[movie_title]['Rating'] = movie_rating
        movie_dict[movie_title]['Main Actor/Actress'] = primary_star
        movie_dict[movie_title]['Supporting Actor/Actress'] = secondary_star
        movie_dict[movie_title]['Metascore'] = metascore_rating
        movie_dict[movie_title]['Gross Earnings in USA'] = final_USA_gross_earnings

        #---------------Director Dictionary-------------------------------
        director_dict[director_name] = {}
        director_dict[director_name]['Birthplace'] = director_birthplace
        director_dict[director_name]['Awards'] = director_oscars
        director_dict[director_name]['First Movie Known For'] = known_for[0]
        director_dict[director_name]['Second Movie Known For'] = known_for[1]
        director_dict[director_name]['Third Movie Known For'] = known_for[2]
        director_dict[director_name]['Fourth Movie Known For'] = known_for[3]

        #---------------Actor/Actress Dictionary-------------------------------
        actor_dict[primary_star_name] = {}
        actor_dict[primary_star_name]['Title'] = primary_star_actor_actress
        actor_dict[primary_star_name]['Awards'] = primary_oscars
        if len(primary_known_for) == 4:
            actor_dict[primary_star_name]['First Media Known For'] = primary_known_for[0]
            actor_dict[primary_star_name]['Second Media Known For'] = primary_known_for[1]
            actor_dict[primary_star_name]['Third Media Known For'] = primary_known_for[2]
            actor_dict[primary_star_name]['Fourth Media Known For'] = primary_known_for[3]
        elif len(primary_known_for) == 3:
            actor_dict[primary_star_name]['First Media Known For'] = primary_known_for[0]
            actor_dict[primary_star_name]['Second Media Known For'] = primary_known_for[1]
            actor_dict[primary_star_name]['Third Media Known For'] = primary_known_for[2]
            actor_dict[primary_star_name]['Fourth Media Known For'] = None
        elif len(primary_known_for) == 2:
            actor_dict[primary_star_name]['First Media Known For'] = primary_known_for[0]
            actor_dict[primary_star_name]['Second Media Known For'] = primary_known_for[1]
            actor_dict[primary_star_name]['Third Media Known For'] = None
            actor_dict[primary_star_name]['Fourth Media Known For'] = None
        else:
            actor_dict[primary_star_name]['First Media Known For'] = primary_known_for[0]
            actor_dict[primary_star_name]['Second Media Known For'] = None
            actor_dict[primary_star_name]['Third Media Known For'] = None
            actor_dict[primary_star_name]['Fourth Media Known For'] = None
        actor_dict[secondary_star_name] = {}
        actor_dict[secondary_star_name]['Title'] = secondary_star_actor_actress
        actor_dict[secondary_star_name]['Awards'] = secondary_oscars
        if len(secondary_known_for) == 4:
            actor_dict[secondary_star_name]['First Media Known For'] = secondary_known_for[0]
            actor_dict[secondary_star_name]['Second Media Known For'] = secondary_known_for[1]
            actor_dict[secondary_star_name]['Third Media Known For'] = secondary_known_for[2]
            actor_dict[secondary_star_name]['Fourth Media Known For'] = secondary_known_for[3]
        elif len(secondary_known_for) == 3:
            actor_dict[secondary_star_name]['First Media Known For'] = secondary_known_for[0]
            actor_dict[secondary_star_name]['Second Media Known For'] = secondary_known_for[1]
            actor_dict[secondary_star_name]['Third Media Known For'] = secondary_known_for[2]
            actor_dict[secondary_star_name]['Fourth Media Known For'] = None
        elif len(secondary_known_for) == 2:
            actor_dict[secondary_star_name]['First Media Known For'] = secondary_known_for[0]
            actor_dict[secondary_star_name]['Second Media Known For'] = secondary_known_for[1]
            actor_dict[secondary_star_name]['Third Media Known For'] = None
            actor_dict[secondary_star_name]['Fourth Media Known For'] = None
        else:
            actor_dict[secondary_star_name]['First Media Known For'] = secondary_known_for[0]
            actor_dict[secondary_star_name]['Second Media Known For'] = None
            actor_dict[secondary_star_name]['Third Media Known For'] = None
            actor_dict[secondary_star_name]['Fourth Media Known For'] = None
    tuple_dict = (movie_dict, director_dict, actor_dict)

    return tuple_dict


#-------------------------------------------------------------------------------
# Put data into a database
DBNAME = 'imdb.db'
def init_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Connection error.")

    check_movie_table = 'DROP TABLE IF EXISTS "Movies"'
    check_director_table = 'DROP TABLE IF EXISTS "Directors"'
    check_actor_table = 'DROP TABLE IF EXISTS "Actors"'


    cur.execute(check_movie_table)
    cur.execute(check_director_table)
    cur.execute(check_actor_table)
    conn.commit()


    movies_statement = '''
    CREATE TABLE IF NOT EXISTS 'Movies' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'MovieName' TEXT NOT NULL,
    'Genre' TEXT NOT NULL,
    'Year' INTEGER NOT NULL,
    'StoryLine' TEXT,
    'MovieScore' REAL NOT NULL,
    'Length' INTEGER NOT NULL,
    'Director' TEXT NOT NULL,
    'DirectorId' INTEGER,
    'Rating' TEXT,
    'LeadName' TEXT NOT NULL,
    'SupportingName' TEXT NOT NULL,
    'Metascore' INTEGER,
    'GrossUSAEarnings' TEXT
    );
    '''

    cur.execute(movies_statement)
    conn.commit()

    directors_statement = '''
    CREATE TABLE IF NOT EXISTS 'Directors' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'DirectorName' TEXT NOT NULL,
    'Birthplace' TEXT,
    'Awards' TEXT,
    'KnownFor1' TEXT,
    'KnownFor2' TEXT,
    'KnownFor3' TEXT,
    'KnownFor4' TEXT
    );
    '''

    cur.execute(directors_statement)
    conn.commit()

    actors_statement = '''
    CREATE TABLE IF NOT EXISTS 'Actors' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT NOT NULL,
    'Title' TEXT,
    'Awards' TEXT,
    'KnownFor1' TEXT,
    'KnownFor2' TEXT,
    'KnownFor3' TEXT,
    'KnownFor4' TEXT
    )
    '''

    cur.execute(actors_statement)
    conn.commit()
    conn.close()


def insert_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for moviename in movie_dict.keys():
        MovieName = moviename
        Genre = movie_dict[moviename]['Genre']
        Year = movie_dict[moviename]['Year']
        StoryLine = movie_dict[moviename]['Storyline']
        MovieScore = movie_dict[moviename]['Score out of 10']
        Length = movie_dict[moviename]['Length']
        Director = movie_dict[moviename]['Director']
        Rating = movie_dict[moviename]['Rating']
        LeadName = movie_dict[moviename]['Main Actor/Actress']
        SupportingName = movie_dict[moviename]['Supporting Actor/Actress']
        Metascore = movie_dict[moviename]['Metascore']
        GrossUSAEarnings = movie_dict[moviename]['Gross Earnings in USA']
        insertion = (None, MovieName, Genre, Year, StoryLine, MovieScore, Length, Director, None, Rating, LeadName, SupportingName, Metascore, GrossUSAEarnings)
        statement = '''
            INSERT INTO 'Movies'
            Values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, insertion)
    conn.commit()

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for directorname in director_dict.keys():
        DirectorName = directorname
        Birthplace = director_dict[directorname]['Birthplace']
        Awards = director_dict[directorname]['Awards']
        KnownFor1 = director_dict[directorname]['First Movie Known For']
        KnownFor2 = director_dict[directorname]['Second Movie Known For']
        KnownFor3 = director_dict[directorname]['Third Movie Known For']
        KnownFor4 = director_dict[directorname]['Fourth Movie Known For']
        insertion = (None, DirectorName, Birthplace, Awards, KnownFor1, KnownFor2, KnownFor3, KnownFor4)
        statement = '''
            INSERT INTO 'Directors'
            Values (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(statement, insertion)
    conn.commit()

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for actorname in actor_dict.keys():
        Name = actorname
        Title = actor_dict[actorname]['Title']
        Awards = actor_dict[actorname]['Awards']
        KnownFor1 = actor_dict[actorname]['First Media Known For']
        KnownFor2 = actor_dict[actorname]['Second Media Known For']
        KnownFor3 = actor_dict[actorname]['Third Media Known For']
        KnownFor4 = actor_dict[actorname]['Fourth Media Known For']
        insertion = (None, Name, Title, Awards, KnownFor1, KnownFor2, KnownFor3, KnownFor4)
        statement = '''
            INSERT INTO 'Actors'
            Values (?, ?, ?, ?, ?, ?, ?, ?)
         '''
        cur.execute(statement, insertion)
    conn.commit()

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement_update = '''
    UPDATE Movies
    SET DirectorId = (
        SELECT Id
        FROM Directors
        WHERE Movies.Director = Directors.DirectorName
    )
    '''
    cur.execute(statement_update)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    get_data()
    init_db()
    insert_data()
    print(movie_dict)
    print(actor_dict)
    print(director_dict)

help_commands = '''
HELP COMMANDS-------------------------------------------------------------------
         1. movie
            -----> prompts user to then input a movie
            -----> if movie is in 250 movies on IMDB it will return information
                   on the movie
         2. graphs
            -----> prompts user to choose between 4 different displays
            -----> the four commands are 'lead',
            A. 'lead'
                -----> displays the top 10 actors/actresses who have appeared
                       the most times in the top 250 movies on IMDB in a bar
                       chart
            B. 'genre'
                -----> displays how many movies of each genre there are in the
                       top 250 movies on IMDB in a pie chart
            C. 'director'
                -----> displays, in a side-by-side bar chart, the top 20
                       directors from California and New York who appeared in
                       the most movies in the top 250 movies on IMDB
            D. 'Actor/Actress'
                -----> displays, in a pie chart, how many of the aggregated lead
                       and supporting roles are played by actors and how many
                       are played by actresses in the top 250 movies on IMDB
         3. exit
            -----> exits the program
         4. help
            -----> lists instructions on what to type into command line
HELP COMMANDS-------------------------------------------------------------------
'''

while True:
    user_input = input("Enter command: ")
    if user_input == 'movie':
        user_input = input("Enter a movie title: ")
        if user_input in movie_dict:
            movie_input_title = user_input
            movie_input_year = movie_dict[user_input]['Year']
            movie_input_genre = movie_dict[user_input]['Genre']
            movie_input_rating = movie_dict[user_input]['Rating']
            movie_input_length = movie_dict[user_input]['Length']
            movie_input_storyline = movie_dict[user_input]['Storyline']
            movie_input_score = movie_dict[user_input]['Score out of 10']
            movie_input_director = movie_dict[user_input]['Director']
            movie_input_primary = movie_dict[user_input]['Main Actor/Actress']
            movie_input_secondary = movie_dict[user_input]['Supporting Actor/Actress']
            result = "{}({}) {} {} {},\n\nPlot: {}.\n\nIt earned a score of {} out of 10, is directed by {}, and is starring {} and {}!".format(movie_input_title, movie_input_year, movie_input_genre, movie_input_rating, movie_input_length, movie_input_storyline, movie_input_score, movie_input_director, movie_input_primary, movie_input_secondary)
            print(result)
        else:
            print("Movie is not in the Top 250 Movies on IMDB. Back to commands")

    elif user_input == 'graphs':
        user_input = input("Enter a command for 1 of the 4 displays: ")
        if user_input == 'lead':
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query1 = '''
            SELECT LeadName
            FROM Movies
            GROUP BY LeadName
            ORDER BY Count(*) DESC
            LIMIT 10
            '''
            cur.execute(query1)
            lst_names = cur.fetchall()

            query2 = '''
            SELECT Count(*)
            FROM Movies
            GROUP BY LeadName
            ORDER BY Count(*) DESC
            LIMIT 10
            '''
            cur.execute(query2)
            lst_count = cur.fetchall()
            conn.close()

            data = [go.Bar(
            x=lst_names,
            y=lst_count
            )]

            layout = go.Layout(
            title="Top 10 Actor/Actresses who have Appeared in the Most Leading Roles in the Top 250 Movies",
            height=500,
            width=1000
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='basic-bar')

        elif user_input == 'genre':
            # Genres: Drama, Action, Adventure, Comedy, Crime, Fantasy, Horror, Mystery, Romance
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_drama = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Drama%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_drama)
            drama_fetchall = cur.fetchall()
            drama_count = 0
            for row in drama_fetchall:
                drama_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_action = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Action%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_action)
            action_fetchall = cur.fetchall()
            action_count = 0
            for row in action_fetchall:
                action_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_adventure = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Adventure%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_adventure)
            adventure_fetchall = cur.fetchall()
            adventure_count = 0
            for row in adventure_fetchall:
                adventure_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_comedy = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Comedy%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_comedy)
            comedy_fetchall = cur.fetchall()
            comedy_count = 0
            for row in comedy_fetchall:
                comedy_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_crime = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Crime%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_crime)
            crime_fetchall = cur.fetchall()
            crime_count = 0
            for row in crime_fetchall:
                crime_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_fantasy = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Fantasy%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_fantasy)
            fantasy_fetchall = cur.fetchall()
            fantasy_count = 0
            for row in fantasy_fetchall:
                fantasy_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_horror = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Horror%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_horror)
            horror_fetchall = cur.fetchall()
            horror_count = 0
            for row in horror_fetchall:
                horror_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_mystery = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Mystery%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_mystery)
            mystery_fetchall = cur.fetchall()
            mystery_count = 0
            for row in mystery_fetchall:
                mystery_count += row[1]

            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query_romance = '''
            SELECT Genre, Count(*)
            FROM Movies
            GROUP BY Genre
            HAVING Genre LIKE '%Romance%'
            ORDER BY Count(*) DESC
            '''
            cur.execute(query_romance)
            romance_fetchall = cur.fetchall()
            romance_count = 0
            for row in romance_fetchall:
                romance_count += row[1]
            conn.close()

            data = [go.Bar(
            x=['Drama', 'Action', 'Adventure', 'Comedy', 'Crime', 'Fantasy', 'Horror', 'Mystery', 'Romance'],
            y=[drama_count, action_count, adventure_count, comedy_count, crime_count, fantasy_count, horror_count, mystery_count, romance_count]
            )]

            layout = go.Layout(
            title="Number of Movies in the Top 250 for Each Main Genre",
            height=400,
            width=750
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='basic-bar')

        elif user_input == 'director':
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            queryny1 = '''
            SELECT Director
            FROM Movies
            JOIN Directors
            ON Movies.Director = Directors.DirectorName
            GROUP BY Director
            HAVING Directors.Birthplace LIKE '%New York%'
            ORDER BY Count(*) DESC
            LIMIT 20
            '''
            cur.execute(queryny1)
            ny_lst_names_fetch = cur.fetchall()
            ny_lst_names = []
            for x in ny_lst_names_fetch:
                ny_lst_names.append(x[0])


            queryny2 = '''
            SELECT Count(*)
            FROM Movies
            JOIN Directors
            ON Movies.Director = Directors.DirectorName
            GROUP BY Director
            HAVING Directors.Birthplace LIKE '%New York%'
            ORDER BY Count(*) DESC
            LIMIT 20
            '''
            cur.execute(queryny2)
            ny_lst_count_fetch = cur.fetchall()
            ny_lst_count = []
            for x in ny_lst_count_fetch:
                ny_lst_count.append(x[0])


            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            querycal1 = '''
            SELECT Director
            FROM Movies
            JOIN Directors
            ON Movies.Director = Directors.DirectorName
            GROUP BY Director
            HAVING Directors.Birthplace LIKE '%California%'
            ORDER BY Count(*) DESC
            LIMIT 20
            '''
            cur.execute(querycal1)
            cal_lst_names_fetch = cur.fetchall()
            cal_lst_names = []
            for x in cal_lst_names_fetch:
                cal_lst_names.append(x[0])


            querycal2 = '''
            SELECT Count(*)
            FROM Movies
            JOIN Directors
            ON Movies.Director = Directors.DirectorName
            GROUP BY Director
            HAVING Directors.Birthplace LIKE '%California%'
            ORDER BY Count(*) DESC
            LIMIT 20
            '''
            cur.execute(querycal2)
            cal_lst_count_fetch = cur.fetchall()
            cal_lst_count = []
            for x in cal_lst_count_fetch:
                cal_lst_count.append(x[0])

            conn.close()

            trace1 = go.Bar(
                x=ny_lst_names,
                y=ny_lst_count,
                name='New York Directors'
            )

            trace2 = go.Bar(
                x=cal_lst_names,
                y=cal_lst_count,
                name='California Directors'
            )

            data = [trace1, trace2]
            layout = go.Layout(
                barmode='group',
                title='Top 20 Directors who have Appeard in the Most Top 250 Movies on IMDB: California vs. New York'
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='grouped-bar')


        elif user_input == 'Actor/Actress':
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            query1 = '''
            SELECT Count(*)
            FROM Actors
            WHERE Title = 'Actor'
            '''
            cur.execute(query1)
            actor_fetch = cur.fetchall()
            for x in actor_fetch:
                actor_number = int(x[0])

            query2 = '''
            SELECT Count(*)
            FROM Actors
            WHERE Title = 'Actress'
            '''
            cur.execute(query2)
            actress_fetch = cur.fetchall()
            for x in actress_fetch:
                actress_number = int(x[0])
            conn.close()

            labels = ['Actors in Leading and Supporting Roles','Actresses in Leading and Supporting Roles']
            values = [actor_number, actress_number]

            trace = go.Pie(labels=labels, values=values)
            py.plot([trace], filename='basic_pie_chart')

        else:
            print("Incorrect display command. Enter a correct command or enter help for list of commands.")

    elif user_input == 'exit':
        print("Thank you! Goodbye.")
        break

    elif user_input == 'help':
        print(help_commands)
        continue

    else:
        print("Invalid command. Please enter a correct command or enter help to see list of commands")
