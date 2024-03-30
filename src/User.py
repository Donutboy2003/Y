class User:
    usr: int = None
    pwd: str = None
    name: str = None
    email: str = None
    city: str = None
    timezone: int = None

    def __init__(self, usr, pwd, name, email, city, timezone):
        self.usr = usr
        self.pwd = pwd
        self.name = name
        self.email = email
        self.city = city
        self.timezone = timezone
