import sqlite3
import sys

from prettytable import PrettyTable
from Tweet import Tweet
from User import User
import random
from datetime import datetime


class App:
    connection = None
    cursor = None
    usr = None

    __last_tweet_id = None

    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys=ON;")
        self.connection.commit()

        self.cursor.execute("SELECT MAX(tid) FROM tweets")
        self.__last_tweet_id = self.cursor.fetchone()[0]

    # LOGIN / SIGN UP #

    def login(self, usr: int, pwd: str) -> bool:
        """
        Check if the user exists and the password matches.
        :param usr: User ID
        :param pwd: Password
        :return: True if login is successful, False otherwise
        """

        login_qry = """
            SELECT usr
            FROM users
            WHERE usr = :usr AND pwd = :pwd
        """

        self.cursor.execute(login_qry, {"usr": usr, "pwd": pwd})
        result = self.cursor.fetchall()

        if len(result) > 0:
            self.usr = usr
            return True

        return False

    def sign_up(
        self, name: str, email: str, city: str, timezone: int, password: str
    ) -> bool:
        """
        Create a new user using the given info. User ID must be generated.
        :param name:
        :param email:
        :param city:
        :param timezone:
        :param password:
        :return: True if sign up is successful, False otherwise
        """
        usr = None

        try:
            while True:
                usr = random.randint(100000, 999999)

                check_id_exists_qry = """
                    SELECT usr
                    FROM users
                """

                self.cursor.execute(check_id_exists_qry)
                result = self.cursor.fetchall()
                if usr not in result:
                    print(usr)
                    break

            data = (usr, password, name, email, city, timezone)
            self.cursor.execute(
                "INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (?,?,?,?,?,?);",
                data,
            )
            self.connection.commit()

            self.login(usr, password)

            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    def logout(self) -> bool:
        """
        Log the user out of the session.
        :return: True if logout was successful, False otherwise
        """
        self.usr = None
        return True

    # USER INTERFACE #

    def show_tweets(self, tweets: list) -> (str, int):
        """
        Display the given list of tweets to the user.
        :param tweets: List of tweets to be displayed
        :return:
        """
        table = PrettyTable()
        table.field_names = ["tid", "write", "date", "reply_to", "text"]
        table.max_width["text"] = 50
        table.max_width["write"] = 25
        table.max_width["reply_to"] = 25
        for tweet in tweets:
            table.add_row(
                [
                    tweet.tid,
                    tweet.writer,
                    tweet.date.strftime("%Y-%m-%d"),
                    tweet.reply_to,
                    tweet.text,
                ],
                divider=True,
            )

        return table.get_string(), len(table.rows)

    def show_users(self, users: list) -> None:
        """
        Display the given list of users to the user.
        :param users: List of users to be displayed
        :return:
        """
        table = PrettyTable()
        table.field_names = ["User ID", "Name", "Email", "City", "Timezone"]
        table.max_width["Name"] = 25
        table.max_width["User ID"] = 25
        table.max_width["Email"] = 25
        table.max_width["City"] = 25
        table.max_width["Timezone"] = 25
        for user in users:
            table.add_row(
                [user.usr, user.name, user.email, user.city, user.timezone],
                divider=True,
            )


        return table.get_string(), len(table.rows)

    def select_tweet(self, tweet_id: int) -> None:
        """
        Select the specified tweet, and display statistics and option to reply or retweet.
        :param tweet_id:
        :return:
        """
        select_tweet_qry = """
            SELECT *
            FROM tweets
            WHERE tid = :tid
        """
        self.cursor.execute(select_tweet_qry, {"tid": tweet_id})
        tweet = self.cursor.fetchone()
        if tweet is None:
            print("Tweet not found.")
            return
        # Get stats
        tweet_stats_qry = """
        SELECT
            (SELECT COUNT(*) FROM retweets WHERE tid = :tid) AS retweet_count,
            (SELECT COUNT(*) FROM tweets WHERE replyto = :tid) AS reply_count
        """

        self.cursor.execute(tweet_stats_qry, {"tid": tweet_id})
        tweet_stats = self.cursor.fetchone()
        # Display tweet
        table = PrettyTable()
        table.field_names = ["Tweet ID", "Author", "Date", "Text", "Reply To", "Retweets", "Replies"]
        table.add_row([tweet[0], tweet[1], tweet[2], tweet[3], tweet[4], tweet_stats[0], tweet_stats[1]])

    
        return table.get_string(), len(table.rows)
    
    def select_user(self, user_id: int) -> None:
        """
        Select the specified user, and display:
            - number of tweets
            - number of users followed
            - number of followers
            - 3 most recent tweets
        :param user_id:
        :return:
        """
        # Get stats
        user_stats_qry = """
            SELECT
                (SELECT COUNT(*) FROM tweets WHERE writer = :usr) AS tweet_count,
                (SELECT COUNT(*) FROM follows WHERE flwer = :usr) AS following_count,
                (SELECT COUNT(*) FROM follows WHERE flwee = :usr) AS follower_count
        """
        self.cursor.execute(user_stats_qry, {"usr": user_id})
        user_stats = self.cursor.fetchone()

        # Display user stats
        user_stats_table = PrettyTable()
        user_stats_table.field_names = ["User ID", "Tweets", "Following", "Followers"]
        user_stats_table.add_row([user_id, user_stats[0], user_stats[1], user_stats[2]])
        user_stats_table

        # Display recent tweets
        most_recent_tweets = self.get_user_tweets(user_id, 3, 1)
        
        stats = user_stats_table.get_string(), len(user_stats_table.rows)
        recent_tweets = self.show_tweets(most_recent_tweets)


        return stats, recent_tweets

    # TWEETS #

    def get_feed_tweets(self, n: int, page: int) -> list:
        """
        Get `n` tweets, paginated at page `page`.
        :param n:
        :param page:
        :return: List of `Tweet` objects that are in the user's feed
        """

        feed_tweets_qry = """
            WITH following AS (
                SELECT flwee
                FROM follows
                WHERE flwer = :usr
            )
            SELECT *
            FROM tweets
            WHERE writer IN following
            UNION
            SELECT tweets.*
            FROM retweets
            JOIN tweets ON retweets.tid = tweets.tid
            WHERE retweets.usr IN following
            ORDER BY tdate
            LIMIT :lim
            OFFSET :offset
        """
        self.cursor.execute(
            feed_tweets_qry, {"usr": self.usr, "lim": n, "offset": n * (page - 1)}
        )
        results = self.cursor.fetchall()
        tweets: list = []

        for tweet in results:
            tweets.append(
                Tweet(
                    tweet[0],
                    tweet[1],
                    datetime.strptime(tweet[2], "%Y-%m-%d"),
                    tweet[3],
                    tweet[4],
                )
            )

        return tweets

    def get_search_tweets(self, search_query: str, n: int, page: int) -> list:
        """
        Search for tweets based on give query, and get `n` tweets at page `page`.
        :param page:
        :param n:
        :param search_query:
        :return: List of `Tweet` objects matching the search keywords
        """

        keywords = search_query.split()

        search_tweets_qry = ""
        tweets: list = []

        for keyword in keywords:
            if keyword[0] == "#":
                search_tweets_qry = """
                    SELECT *
                    FROM tweets
                    WHERE tid IN (
                        SELECT tid
                        FROM mentions
                        WHERE term LIKE :kw
                    )
                    ORDER BY tdate
                """
                self.cursor.execute(
                    search_tweets_qry,
                    {"kw": keyword[1:], "lim": n, "offset": n * (page - 1)},
                )
            else:
                search_tweets_qry = """
                    SELECT *
                    FROM tweets
                    WHERE text LIKE :kw1 OR text LIKE :kw2 OR text LIKE :kw3 OR text LIKE :kw4 
                       or text LIKE :kw5 OR text LIKE :kw6 OR text LIKE :kw7 OR text LIKE :kw8
                    ORDER BY tdate
                """
                self.cursor.execute(
                    search_tweets_qry,
                    {
                        "kw1": f"% {keyword}",
                        "kw2": f"% {keyword} %",
                        "kw3": f"{keyword} %",
                        "kw4": f"{keyword}",
                        "kw5": f"% #{keyword}",
                        "kw6": f"% #{keyword} %",
                        "kw7": f"#{keyword} %",
                        "kw8": f"#{keyword}",
                        "lim": n,
                        "offset": n * (page - 1),
                    },
                )

            results = self.cursor.fetchall()
            for tweet in results:
                tweets.append(
                    Tweet(
                        tweet[0],
                        tweet[1],
                        datetime.strptime(tweet[2], "%Y-%m-%d"),
                        tweet[3],
                        tweet[4],
                    )
                )

        return tweets[n * (page - 1) : n * (page - 1) + n]

    def compose(self, tweet_text, reply_to=None) -> bool:
        """
        Allow the user to compose a new tweet.
        :return: True if the tweet was successfully composed, False otherwise
        """
        self.__last_tweet_id = self.__last_tweet_id + 1
        tweet_id = self.__last_tweet_id
        current_datetime = datetime.now()
        tweet_date = current_datetime.strftime(
            "%Y-%m-%d"
        )  # to get in the format of YYYY-MM-DD
        tweet_writer = self.usr
        tweet_data = (tweet_id, tweet_writer, tweet_date, tweet_text, reply_to)

        try:
            self.cursor.execute(
                "INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?,?,?,?,?);",
                tweet_data,
            )
            for word in tweet_text.split():
                if word[0] == "#":
                    self.create_hashtag(word[1:])
                    self.mentions(tweet_id, word[1:])
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    def reply(self, reply_id: int) -> bool:
        """
        Special case of `compose()` where the tweet is a reply to another tweet.
        :param reply_id: ID of tweet being replied to
        :return: True if reply was successfully created, False otherwise
        """
        tweet_text = input("Enter the tweet reply text: ")
        self.__last_tweet_id = self.__last_tweet_id + 1
        tweet_id = self.__last_tweet_id
        current_datetime = datetime.now()
        tweet_date = current_datetime.strftime(
            "%Y-%m-%d"
        )  # to get in the format of YYYY-MM-DD
        tweet_replyto = reply_id
        tweet_writer = self.usr
        reply_tweet_data = (
            tweet_id,
            tweet_writer,
            tweet_date,
            tweet_text,
            tweet_replyto,
        )

        hashtags = []

        try:
            self.cursor.execute(
                "INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?,?,?,?,?);",
                reply_tweet_data,
            )
            for word in tweet_text.split():
                if word[0] == "#":
                    self.create_hashtag(word[1:])
                    self.mentions(tweet_id, word[1:])
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    def create_hashtag(self, term) -> bool:
        """
        Create a hashtag using the keyword if it doesn't exist already
        :param term: the keyword of the hashtag
        :return: True if keyword added successfully, False otherwise
        """

        hashtag_search_qry = """
            SELECT term
            FROM hashtags
        """

        self.cursor.execute(hashtag_search_qry)
        result = self.cursor.fetchall()

        for word in result:
            if word[0].lower() == term.lower():
                return False  # return False if keyword is already present?

        try:
            self.cursor.execute("INSERT INTO hashtags (term) VALUES (?);", (term,))
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    def mentions(self, tid, term) -> bool:
        """
        Mention the hashtag in a tweet text.
        :param tid: ID of the tweet mentioning the term
        :param term: The hashtag being mentioned by the tweet
        :return: True if added successfully, False otherwise
        """
        try:
            self.cursor.execute(
                "INSERT INTO mentions (tid,term) VALUES (?,?);", (tid, term)
            )
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    def retweet(self, retweet_id: int) -> bool:
        """
        Retweet the given tweet.
        :param retweet_id: ID of tweet being retweeted
        :return: True if retweeted successfully, False otherwise
        """

        current_datetime = datetime.now()
        tweet_date = current_datetime.strftime(
            "%Y-%m-%d"
        )  # to get in the format of YYYY-MM-DD
        tweet_writer = self.usr
        retweet_data = (tweet_writer, retweet_id, tweet_date)

        try:
            self.cursor.execute(
                "INSERT INTO retweets (usr, tid, rdate) VALUES (?,?,?);", retweet_data
            )
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False

    # USERS #

    def get_user_tweets(self, user_id: int, n: int, page: int) -> list:
        """
        Get `n` tweets at page `page` for the specified user.
        :param user_id:
        :param n:
        :param page:
        :return: List of tweets made by the user
        """

        user_tweets_qry = """
            SELECT *
            FROM tweets
            WHERE writer = :usr
            ORDER BY tdate
            LIMIT :lim
            OFFSET :offset
        """

        self.cursor.execute(
            user_tweets_qry, {"usr": user_id, "lim": n, "offset": n * (page - 1)}
        )
        results = self.cursor.fetchall()
        tweets: list = []

        for tweet in results:
            tweets.append(Tweet(tweet[0], tweet[1], datetime.strptime(tweet[2], "%Y-%m-%d"), tweet[3], tweet[4]))

        return tweets


    def get_search_users(self, keyword: str, n: int, page: int) -> list[User]:
        """
        Search for users by name and city, and get n users at page page.
        :param keyword: The keyword to search for in names and cities
        :param n: Number of users to return per page
        :param page: The page number for paginated results
        :return: List of users that match the search
        """
        user_list: list = []


        search_name_query = """
            SELECT *
            FROM users
            WHERE name LIKE :kw
            ORDER BY LENGTH(name)
        """

        search_city_query = """
            SELECT *
            FROM users 
            WHERE city LIKE :kw AND name NOT LIKE :kw
            ORDER BY LENGTH(city)
        """

    
        self.cursor.execute(search_name_query, {"kw": f"%{keyword}%"})
        results_name = self.cursor.fetchall()

        self.cursor.execute(search_city_query, {"kw": f"%{keyword}%"})
        results_city = self.cursor.fetchall()

        combined_results = list(results_name) + [usr for usr in results_city if usr not in results_name]


        for usr in combined_results:
            user_list.append(User(usr[0], usr[1], usr[2], usr[3], usr[4], usr[5]))

        start_index = n * (page - 1)
        end_index = start_index + n
        paginated_users = user_list[start_index:end_index]

        return paginated_users
    
    
    def follow(self, user_id: int) -> bool:
        """
        Follow the given user.
        :param user_id:
        :return: True if followed successfully, False otherwise
        """
        
        
        check_already_following_qry = """
            SELECT flwee
            FROM follows
            WHERE flwer = :flwer AND flwee = :flwee
        """

        self.cursor.execute(check_already_following_qry, {"flwer": self.usr, "flwee": user_id})
        result = self.cursor.fetchall()

        if len(result) > 0:
            return False #followee already being followed
        
        if self.usr == user_id:
            return False
        
        flwee_id = user_id
        flwer_id =self.usr
        current_datetime = datetime.now()
        follow_date = current_datetime.strftime("%Y-%m-%d") #to get in the format of YYYY-MM-DD
        follow_data = (flwer_id,flwee_id,follow_date)

        try:
            self.cursor.execute('INSERT INTO follows (flwer, flwee, start_date) VALUES (?,?,?);', follow_data)
            self.connection.commit()
            return True
        
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False
        
    def get_followers(self, n: int, page: int = 1) -> list:
        """
        List all users that follow the currently logged-in user, getting `n` of such users at page `page`.
        :param n:
        :param page:
        :return: List of `n` users at `page`
        """
        followers_qry = """
            SELECT u.*
            FROM users u
            JOIN follows f ON f.flwer = u.usr
            WHERE flwee = :usr
            LIMIT :lim
            OFFSET :offset
        """

        self.cursor.execute(
            followers_qry, {"usr": self.usr, "lim": n, "offset": n * (page - 1)}
        )
        results = self.cursor.fetchall()
        users: list = []

        for user in results:
            print(user)
            users.append(User(user[0], None, user[2], user[3], user[4], user[5]))

        return users


if __name__ == "__main__":
    app = App("../db/database.db")
    app.login(2, "def")
    f = app.get_followers(5, 1)
    print(app.show_users(f))
