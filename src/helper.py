import curses


def add_str_centered(stdscr, cols: int, y: int, s: str):
    x = (cols - len(s)) // 2
    stdscr.addstr(y, x, s)
    stdscr.refresh()


def add_footer(stdscr, cols: int, lines: int, s: str):
    stdscr.move(lines - 2, 0)
    stdscr.clrtoeol()
    add_str_centered(stdscr, cols, lines - 2, s)


def add_rec(stdscr, curses, width, height, y, x):
    curses.textpad.rectangle(stdscr, y, x, y + height, x + width)


def tweets_footer(n_rows, page, feed=False, followers=True):
    footer = ""
    if n_rows == 5:
        footer += "[n] Next page"
    if page > 1:
        footer += "  [p] Previous page"
    if feed:
        footer += "  [f] Show feed"

    footer += (
        "  [i] Select <id>  [s] Search tweets  [u] Search users  [c] Compose tweet"
    )
    if followers:
        footer += "  [g] View followers"
    footer += "  [x] Log out  [q] Quit"

    return footer
