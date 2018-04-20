# --------------------------SCRAP WORK ------------------------------#


        #------------------------------------------------------------
        # call each class and append them to lists
        # movie_lst = Movies(movie_title, movie_year, movie_score, movie_genre, movie_storyline, movie_director, metascore_rating, movie_rating, primary_star, secondary_star, USA_gross_earnings)
        # movie_listings.append(movie_lst)
        # director_lst = Directors()
        # director_listings.append(director_lst)
        # actor_lst = Actors()
        # actor_listings.append(actor_lst)
    # for x in movie_listings:
    #     print(x)

    # return (movie_listings, director_listings, actor_listings)

        #------------------------------------------------------------





        #-------------------------------------------------------------------------------
        # Making Classes to Extract Data
        # class Movies():
        #     def __init__(self, movie_title, movie_year, movie_score, movie_genre, movie_storyline, movie_director, metascore_rating, movie_rating, primary_star, secondary_star, USA_gross_earnings):
        #         self.title = movie_title
        #         # self.url = movie_information
        #         self.movie_year = movie_year
        #         self.movie_score = movie_score
        #         self.genre = movie_genre
        #         self.storyline = movie_storyline
        #         self.director = movie_director
        #         self.metascore = metascore_rating
        #         self.movie_rating = movie_rating
        #         self.main = primary_star
        #         self.supporting = secondary_star
        #         self.gross_earnings = USA_gross_earnings[12:]
        #
        #     def __str__(self):
        #         return "{}({}) earned a rating of {} out of 10".format(self.title, self.movie_year, self.movie_score)

        # class Directors():
        #     def __init__(self):
        #
        #
        # class Actors():
        #     def __init__(self):
        #-------------------------------------------------------------------------------









            #############################################
            # clarification of variables for dictionary
            #           --Movie Table---
            # for movie titles -----> movie_title
            # for movie years -----> movie_year
            # for movie scores by imdb users -----> movie_score
            # for movie lengths -----> movie_length
            # for movie genres -----> movie_genre
            # for name of movie director -----> movie_director
            # for rating of movie(ex. PG) -----> movie_rating
            # for name of primary star in movie -----> primary_star
            # for name of secondary star in movie -----> secondary_star
            # for metascore rating of movie -----> metascore_rating
            # for storyline of movie -----> movie_storyline
            # for the gross earnings in USA of movie  -----> USA_gross_earnings


            #          --Director Table--
            # for name of movie director  -----> director_name
            # for director of movies birthplace -----> director_birthplace
            # for awards won by director of movie -----> director_oscars
            # list of movies director is known for -----> known_for


            #          --Actors Table--
            # for name of primary star in movie -----> primary_star_name
            # for name of secondary star in movie-----> secondary_star_name
            # says whether primary star is an actor or an actress -----> primary_star_actor_actress
            # says whether secondary star is an actor or an actress -----> secondary_star_actor_actress
            # says what awards primary star of movie has won -----> primary_oscars
            # says what awards secondary star of movie has won  -----> secondary_oscars
            # list of movies that primary star is known for -----> primary_known_for
            # list of movies that secondary star is known for -----> secondary_known_for

            #        ---Advice from GSI--
            # for x in class is how you will get away from the objects and ge the string to print out
            # can strip away newline
            # use if statements (ex. if not none or if not 0) to get blank values in table
            # made requirements.txt file but it really is for people using flask
            # keep length values the same
