import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


print(engine)
f = open("books.csv")
reader = csv.reader(f)

for isbn, title, author, year in reader:
    #The if statement sole purpose is to skip the first line containg the column one of which is 'isbn'
    if not isbn == "isbn":
        db.execute('INSERT INTO "book" (isbn, title, author, year) VALUES (:ISBN, :title, :author, :year)',
                    {"ISBN": isbn, "title": title, "author": author, "year":year})
        print(f" The book '{title}' - with ISBN {isbn} was added to the database.")

db.commit()

