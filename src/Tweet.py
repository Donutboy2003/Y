from datetime import datetime


class Tweet:
    tid: int = None
    writer: int = None
    date: datetime = None
    text: str = None
    reply_to: int = None

    def __init__(self, tid, writer, date, text, reply_to):
        self.tid = tid
        self.writer = writer
        self.date = date
        self.text = text
        self.reply_to = reply_to

    def __str__(self):
        return f"Tweet {self.tid} by {self.writer} on {self.date} to {self.reply_to}: {self.text}"

    def __lt__(self, other):
        return self.date < other.date
