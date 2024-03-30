import curses
import curses.textpad
import sys
import time
import traceback

from App import App
from helper import *


def show_splash(app):
    stdscr.clear()

    add_footer(stdscr, curses.COLS, curses.LINES, "[q] Quit")

    add_str_centered(stdscr, curses.COLS, curses.LINES // 2 - 3, "Welcome to Y")
    add_str_centered(stdscr, curses.COLS, curses.LINES // 2 - 1, "[1] Log In")
    add_str_centered(stdscr, curses.COLS, curses.LINES // 2 - 0, "[2] Sign Up")

    while True:
        c = stdscr.getch()
        if c == ord("q"):
            break
        if c == ord("1"):
            show_login(app)
        if c == ord("2"):
            show_signup(app)


def show_login(app):
    stdscr.clear()

    top_left_x = curses.COLS // 2 - 15
    top_left_y = curses.LINES // 2 - 3
    add_rec(stdscr, curses, 30, 6, top_left_y, top_left_x)
    stdscr.addstr(top_left_y, top_left_x + 2, " LOGIN ")
    stdscr.addstr(top_left_y + 2, top_left_x + 2, "User ID: ")
    stdscr.addstr(top_left_y + 4, top_left_x + 2, "Password: ")

    curses.echo()
    curses.curs_set(1)
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering User ID...")
    usr = stdscr.getstr(top_left_y + 2, top_left_x + 2 + 9, 6)
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Password...")
    curses.noecho()
    pwd = stdscr.getstr(top_left_y + 4, top_left_x + 2 + 10).decode("utf-8")
    curses.curs_set(0)

    try:
        usr = int(usr)
    except ValueError:
        raise ValueError("User ID must be an integer")

    stdscr.clear()

    if app.login(usr, pwd):
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Login successful.")
        stdscr.refresh()
        time.sleep(1)
        show_feed(app)
    else:
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Login failed.")
        stdscr.refresh()
        time.sleep(1)
        show_splash(app)


def show_signup(app):
    stdscr.clear()

    top_left_x = curses.COLS // 2 - 15
    top_left_y = curses.LINES // 2 - 6
    add_rec(stdscr, curses, 30, 12, top_left_y, top_left_x)
    stdscr.addstr(top_left_y, top_left_x + 2, " SIGN UP ")
    stdscr.addstr(top_left_y + 2, top_left_x + 2, "Name: ")
    stdscr.addstr(top_left_y + 4, top_left_x + 2, "Email: ")
    stdscr.addstr(top_left_y + 6, top_left_x + 2, "City: ")
    stdscr.addstr(top_left_y + 8, top_left_x + 2, "Timezone: ")
    stdscr.addstr(top_left_y + 10, top_left_x + 2, "Password: ")

    curses.echo()
    curses.curs_set(1)
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Name...")
    name = stdscr.getstr(top_left_y + 2, top_left_x + 2 + 6).decode("utf-8")
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Email...")
    email = stdscr.getstr(top_left_y + 4, top_left_x + 2 + 7).decode("utf-8")
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering City...")
    city = stdscr.getstr(top_left_y + 6, top_left_x + 2 + 6).decode("utf-8")
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Timezone...")
    timezone = stdscr.getstr(top_left_y + 8, top_left_x + 2 + 10).decode("utf-8")
    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Password...")
    curses.noecho()
    password = stdscr.getstr(top_left_y + 10, top_left_x + 2 + 10).decode("utf-8")
    curses.curs_set(0)

    try:
        timezone = int(timezone)
    except ValueError:
        raise ValueError("timezone must be a positive or negative integer")

    stdscr.clear()

    if app.sign_up(name, email, city, timezone, password):
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Sign up successful.")
        stdscr.refresh()
        time.sleep(1)
        show_feed(app)
    else:
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Sign up failed.")
        stdscr.refresh()
        time.sleep(1)
        show_splash(app)


def show_feed(app, page=1):
    stdscr.clear()
    add_str_centered(stdscr, curses.COLS, 3, "USER FEED")
    feed_tweets = app.get_feed_tweets(5, page)
    table, n_rows = app.show_tweets(feed_tweets)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(stdscr, curses.COLS, curses.LINES, tweets_footer(n_rows, page))

    while True:
        c = stdscr.getch()
        if c == ord("n") and n_rows == 5:
            show_feed(app, page + 1)
        if c == ord("p") and page > 1:
            show_feed(app, page - 1)
        if c == ord("i"):
            n = int(stdscr.getstr())
            valid_ids = [tweet.tid for tweet in feed_tweets]
            if n in valid_ids:
                select_tweet(app, n)
        if c == ord("s"):
            show_search_results(app)
        if c == ord("u"):
            show_user_search_results(app)
        if c == ord("c"):
            show_tweet_compose(app)
        if c == ord("g"):
            show_followers(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            sys.exit()


def show_user_tweets(app, id, page=1):
    stdscr.clear()
    add_str_centered(stdscr, curses.COLS, 3, "User Tweets")
    user_tweets = app.get_user_tweets(id, 5, page)
    table, n_rows = app.show_tweets(user_tweets)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(stdscr, curses.COLS, curses.LINES, tweets_footer(n_rows, page))

    while True:
        c = stdscr.getch()
        if c == ord("n") and n_rows == 5:
            show_user_tweets(app, page + 1)
        if c == ord("p") and page > 1:
            show_user_tweets(app, page - 1)
        if c == ord("i"):
            n = int(stdscr.getstr())
            valid_ids = [tweet.tid for tweet in user_tweets]
            if n in valid_ids:
                select_tweet(app, n)
        if c == ord("s"):
            show_search_results(app)
        if c == ord("u"):
            show_user_search_results(app)
        if c == ord("c"):
            show_tweet_compose(app)
        if c == ord("g"):
            show_followers(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            sys.exit()


def get_search_qry():
    stdscr.clear()

    top_left_x = (curses.COLS - (curses.COLS - 5)) // 2
    top_left_y = curses.LINES // 2 - 2
    add_rec(stdscr, curses, curses.COLS - 5, 4, top_left_y, top_left_x)
    stdscr.addstr(top_left_y, top_left_x + 2, " SEARCH ")

    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Search Query...")

    curses.echo()
    curses.curs_set(1)
    search_qry = stdscr.getstr(top_left_y + 2, top_left_x + 2).decode("utf-8")
    curses.noecho()
    curses.curs_set(0)

    stdscr.clear()
    return search_qry


def get_user_search_qry():
    stdscr.clear()

    top_left_x = (curses.COLS - (curses.COLS - 5)) // 2
    top_left_y = curses.LINES // 2 - 3
    add_rec(stdscr, curses, curses.COLS - 5, 4, top_left_y, top_left_x)
    stdscr.addstr(top_left_y, top_left_x + 2, " QUERY ")

    # top_left_y = curses.LINES // 2 + 3
    # add_rec(stdscr, curses, curses.COLS - 5, 4, top_left_y, top_left_x)
    # stdscr.addstr(top_left_y, top_left_x + 2, " SEARCH CITIES ")

    add_footer(stdscr, curses.COLS, curses.LINES, "Entering Search Query...")

    curses.echo()
    curses.curs_set(1)
    names_qry = stdscr.getstr(top_left_y + 2, top_left_x + 2).decode("utf-8")
    # cities_qry = stdscr.getstr(top_left_y + 2, top_left_x + 2).decode("utf-8")
    curses.noecho()
    curses.curs_set(0)

    if not names_qry: 
        stdscr.clear()
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Invalid query.")
        stdscr.refresh()
        time.sleep(1)
        names_qry = get_user_search_qry()

    stdscr.clear()
    return names_qry


def show_tweet_compose(app, reply_to=None):
    stdscr.clear()

    top_left_x = (curses.COLS - (curses.COLS - 5)) // 2
    top_left_y = curses.LINES // 2 - 3
    add_rec(stdscr, curses, curses.COLS - 5, 6, top_left_y, top_left_x)
    stdscr.addstr(top_left_y, top_left_x + 2, " COMPOSE ")

    add_footer(stdscr, curses.COLS, curses.LINES, "Composing Tweet...")

    curses.echo()
    curses.curs_set(1)
    tweet_txt = stdscr.getstr(top_left_y + 2, top_left_x + 2).decode("utf-8")
    curses.noecho()
    curses.curs_set(0)

    if not tweet_txt: 
        stdscr.clear()
        add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Invalid text.")
        stdscr.refresh()
        time.sleep(1)
        names_qry = show_tweet_compose(app, reply_to)


    add_footer(
        stdscr, curses.COLS, curses.LINES, "[s] Post  [e] Rewrite  [c] Cancel  [q] Quit"
    )

    while True:
        c = stdscr.getch()
        if c == ord("s"):
            app.compose(tweet_txt, reply_to)
            stdscr.clear()
            add_str_centered(stdscr, curses.COLS, curses.LINES // 2, "Tweet posted.")
            stdscr.refresh()
            time.sleep(1)
            show_feed(app)
        if c == ord("e"):
            show_tweet_compose(app)
        if c == ord("c"):
            show_feed(app)
        if c == ord("q"):
            break


def show_search_results(app, page=1, search_qry=None):
    stdscr.clear()
    stdscr.refresh()

    if search_qry is None:
        search_qry = get_search_qry()

    search_tweets = app.get_search_tweets(search_qry, 5, page)
    add_str_centered(stdscr, curses.COLS, 3, f"SEARCH RESULTS: '{search_qry}'")

    table, n_rows = app.show_tweets(search_tweets)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(stdscr, curses.COLS, curses.LINES, tweets_footer(n_rows, page, True))

    while True:
        c = stdscr.getch()
        if c == ord("n") and n_rows == 5:
            show_search_results(app, page + 1, search_qry)
        if c == ord("p") and page > 1:
            show_search_results(app, page - 1, search_qry)
        if c == ord("i"):
            n = int(stdscr.getstr())
            valid_ids = [tweet.tid for tweet in search_tweets]
            if n in valid_ids:
                select_tweet(app, n)
        if c == ord("f"):
            show_feed(app)
        if c == ord("s"):
            show_search_results(app)
        if c == ord("u"):
            show_user_search_results(app)
        if c == ord("c"):
            show_tweet_compose(app)
        if c == ord("g"):
            show_followers(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            sys.exit()


def show_user_search_results(app, page=1, names_qry=None, cities_qry=None):
    if names_qry is None:
        names_qry = get_user_search_qry()

    stdscr.clear()
    search_users = app.get_search_users(names_qry, 5, page)
    add_str_centered(
        stdscr, curses.COLS, 3, f"SEARCH RESULTS: '{names_qry}'"
    )

    table, n_rows = app.show_users(search_users)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(stdscr, curses.COLS, curses.LINES, tweets_footer(n_rows, page, True))

    while True:
        c = stdscr.getch()
        if c == ord("n") and n_rows == 5:
            show_followers(app, page + 1)
        if c == ord("p") and page > 1:
            show_followers(app, page - 1)
        if c == ord("f"):
            show_feed(app)
        if c == ord("i"):
            n = int(stdscr.getstr())
            valid_ids = [user.usr for user in search_users]
            if n in valid_ids:
                select_user(app, n)
        if c == ord("s"):
            show_search_results(app)
        if c == ord("u"):
            show_user_search_results(app)
        if c == ord("c"):
            show_tweet_compose(app)
        if c == ord("g"):
            show_followers(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            sys.exit()


def show_followers(app, page=1):
    stdscr.clear()
    followers = app.get_followers(5, page)
    add_str_centered(stdscr, curses.COLS, 3, f"FOLLOWERS")

    table, n_rows = app.show_users(followers)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(stdscr, curses.COLS, curses.LINES, tweets_footer(n_rows, page, True))

    while True:
        c = stdscr.getch()
        if c == ord("n") and n_rows == 5:
            show_followers(app, page + 1)
        if c == ord("p") and page > 1:
            show_followers(app, page - 1)
        if c == ord("f"):
            show_feed(app)
        if c == ord("i"):
            n = int(stdscr.getstr())
            valid_ids = [follower.usr for follower in followers]
            if n in valid_ids:
                select_user(app, n)
        if c == ord("s"):
            show_search_results(app)
        if c == ord("u"):
            show_user_search_results(app)
        if c == ord("c"):
            show_tweet_compose(app)
        if c == ord("g"):
            show_followers(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            sys.exit()


def select_tweet(app, id):
    stdscr.clear()
    add_str_centered(stdscr, curses.COLS, 3, "TWEET STATS")
    table, n_rows = app.select_tweet(id)
    table_lines = table.split("\n")
    x = (curses.COLS - len(table_lines[0])) // 2
    y = curses.LINES // 2 - n_rows * 2 + 3 // 2
    for i, line in enumerate(table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(
        stdscr,
        curses.COLS,
        curses.LINES,
        "[r] Reply  [t] Retweet  [f] Show feed  [x] Log out  [q] Quit",
    )

    while True:
        c = stdscr.getch()
        if c == ord("r"):
            show_tweet_compose(app, id)
        if c == ord("t"):
            app.retweet(id)
            stdscr.clear()
            add_str_centered(
                stdscr, curses.COLS, curses.LINES // 2, "Retweet successful."
            )
            stdscr.refresh()
            time.sleep(1)
            show_feed(app)
        if c == ord("f"):
            show_feed(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            break


def select_user(app, id):
    stdscr.clear()
    add_str_centered(stdscr, curses.COLS, 3, "USER STATS")
    user_stats, user_tweets = app.select_user(id)
    stats_table, stats_n_rows = user_stats
    tweets_table, tweets_n_rows = user_tweets
    n_rows = stats_n_rows + tweets_n_rows
    stats_table_lines = stats_table.split("\n")
    tweets_table_lines = tweets_table.split("\n")
    x = (curses.COLS - len(stats_table_lines[0])) // 2
    y = 5
    for i, line in enumerate(stats_table_lines):
        stdscr.addstr(y + i, x, line)
    x = (curses.COLS - len(tweets_table_lines[0])) // 2
    y = curses.LINES // 2 - tweets_n_rows * 2 + 3
    for i, line in enumerate(tweets_table_lines):
        stdscr.addstr(y + i, x, line)

    add_footer(
        stdscr,
        curses.COLS,
        curses.LINES,
        "[r] Follow  [t] Show More  [f] Show feed  [x] Log out  [q] Quit",
    )

    while True:
        c = stdscr.getch()
        if c == ord("r"):
            app.follow(id)
            stdscr.clear()
            add_str_centered(
                stdscr, curses.COLS, curses.LINES // 2, "Follow successful."
            )
            stdscr.refresh()
            time.sleep(1)
            show_feed(app)
        if c == ord("t"):
            show_user_tweets(app, id)
        if c == ord("f"):
            show_feed(app)
        if c == ord("x"):
            app.logout()
            show_splash(app)
        if c == ord("q"):
            break


def main(stdscr):
    try:
        stdscr.clear()

        path = sys.argv[1]
        app = App(path)
        # app = App("../db/database.db")

        show_splash(app)

    except Exception as e:
        stdscr.clear()
        curses.init_pair(1, curses.COLOR_WHITE, 52)
        s = f"  An error occurred: {e}.  "
        stdscr.addstr(
            curses.LINES // 2, curses.COLS // 2 - len(s) // 2, s, curses.color_pair(1)
        )
        add_footer(stdscr, curses.COLS, curses.LINES, "[c] Continue  [q] Quit")
        stdscr.refresh()
        while True:
            c = stdscr.getch()
            if c == ord("c"):
                break
            if c == ord("q"):
                sys.exit()
        main(stdscr)
    finally:
        pass


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    curses.wrapper(main)
