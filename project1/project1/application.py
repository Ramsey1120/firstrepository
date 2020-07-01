import os
import requests
import math

# added redirect,url_for, jsonify to the modules to import
from flask import Flask, session, render_template, redirect, request, url_for, session, jsonify, json
from flask_session import Session
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

# setting the secret key to enecrypt all session data in the server 
app.secret_key = "3_Z26f?0jTV4!"

# making sure JSON doesnt sort the data that I will return with jsonify function
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods = ['POST','GET'])
def signup():
    if request.method == "POST":
        # storing form data into variables
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        #parametirezed insert query to register a user 
        query = db.execute('INSERT INTO "user" (username,email,password) VALUES (:username, :email, :password)',
        {"username":username, "email":email, "password":password})

        #save changes to the database
        db.commit()

        # simple check to verify acoount creation
        if not db.execute('SELECT * FROM "user" WHERE email = :email', {"email":email}).rowcount == 0:
            return render_template("signup.html", message="Account was created. You can now")
        else:
            return render_template("signup.html", message_error="Account wasn't created. Try again")
    else:
        return render_template("signup.html")


           
@app.route("/login", methods = ['POST','GET'])
def login():
    if request.method == "POST":
        # storing form data into variables
        username = request.form.get("username")
        password = request.form.get("password")

        #query to check for matching credentials
        check = db.execute('SELECT * FROM "user" WHERE username=:username AND password=:password', 
        {"username":username, "password":password})
        
        if not check.rowcount == 0:
            #assign data to session variables and then redirect to search page
            for user in check:
                session["userID"] = user.userid
                session["username"] = user.username
                session["password"] = user.password

            return redirect(url_for("search"))
        else:
            # if there were no matching credentials (from th query), return error message
            message = "The username or password is wrong. Try again"
            return render_template("login.html", message=message)

    return render_template("login.html")


@app.route("/searchbook", methods = ['POST','GET'])
def search():
    if request.method == "POST":
        
        # store form data into variables
        isbn = request.form.get("ISBN")
        if isbn == "":
            isbn="/"

        title = request.form.get("title")
        if title == "":
            title="/"

        author = request.form.get("author")
        if author == "":
            author="/"
        
        # query to find all books with matchig credentials to the ones submitted in the form
        books = db.execute('SELECT * FROM "book" WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author',
        {"isbn":"%" + isbn + "%", "title":"%" + title + "%", "author":"%" + author + "%"})

        # if no books were found return message that sugggests so
        if books.rowcount == 0:
            message = "No books were found. Try again"
            return render_template("search.html", message=message)
        else:
            return render_template("search.html", books=books)

    return render_template("search.html", default_message="No books here. Search for one now.")


@app.route("/book/<string:isbn>", methods = ['GET','POST'])
def book(isbn):

    userID = session["userID"]

    # queries to fecth book info and all reviews associated with it 
    book = db.execute('SELECT * FROM "book" WHERE book.isbn = :isbn', {"isbn":isbn})
    reviews = db.execute('SELECT reviewtitle,reviewtext,stars FROM "review" WHERE review.isbn = :isbn', 
    {"isbn":isbn})
    
    # making request to goodreads API
    goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", 
    params={"key": "JKTvp0Q2VbEfsQ3syQmjQ", "isbns": isbn})


    data =  goodreads.json()
    isbns = data["books"][0]["isbn"]
    no_reviews = data["books"][0]["reviews_count"]
    avg_star = data["books"][0]["average_rating"]

    # Storing error messages into variables
    message = "You already wrote a review about this book!"
    message1 = "This book has no reviews. Write yours now!"

    # Checking if the user has written a review on the book
    if db.execute('SELECT * FROM "review" WHERE review.userid = :userID AND review.isbn = :isbn', 
    {"userID":userID, "isbn":isbn}).rowcount == 0:

        #checking if a form submission for the new reviews has been made
        if request.method == "POST":

            #assign variables to form data
            reviewTitle = request.form.get("reviewTitle")
            reviewText = request.form.get("reviewText")
            stars = request.form.get("stars")

            # add the review to the database with a query
            db.execute('INSERT INTO "review" (reviewtitle, reviewtext, stars, isbn, userid) VALUES (:reviewTitle, :reviewText, :stars, :isbn, :userID)', 
            {"reviewTitle": reviewTitle, "reviewText": reviewText, "stars":stars, "isbn":isbn, "userID":userID})

            # saving the changes to the database
            db.commit()

            # select query to show the updated number of book reviews
            reviews = db.execute('SELECT reviewtitle,reviewtext,stars FROM "review" WHERE review.isbn = :isbn',
            {"isbn":isbn})

            message = "You already wrote a review about this book!"

            return render_template("book.html", book = book, reviews =reviews, message=message, avg_star=avg_star, no_reviews=no_reviews, isbn=isbns)

        # checking if the book has any reviews at all
        if reviews.rowcount == 0:
            return render_template("book.html", book = book, reviews = reviews, message1 = message1, avg_star = avg_star, no_reviews = no_reviews, isbn=isbns)
    else:
        return render_template("book.html", book = book, reviews = reviews, message = message, avg_star = avg_star, no_reviews = no_reviews, isbn=isbns)

    return render_template("book.html", book = book, reviews = reviews, avg_star = avg_star, no_reviews = no_reviews, isbn=isbns)



@app.route("/api/<string:isbn>", methods=['GET'])
def goodreads(isbn):
    
    # declaring array to store all relevant book info
    array = list()

    # fetching all info about a book based on the isbn
    book = db.execute('SELECT isbn,title, author, year FROM "book" WHERE isbn=:isbn GROUP BY book.isbn', 
    {"isbn":isbn})

    for i in book:
        array.append(i.isbn)
        array.append(i.title) 
        array.append(i.author)  
        array.append(i.year)    

    # fetching all the reviews of a book based on the isbn
    review = db.execute('SELECT COUNT(reviewid) AS no_reviews, AVG(stars) AS avg_score FROM "review" \
    WHERE review.isbn=:isbn GROUP BY isbn', {"isbn":isbn})

    if not review.rowcount == 0:
        for i in review:
            array.append(i.no_reviews)
            array.append(i.avg_score)
    else:
        array.append(0)
        array.append(0)

    # returning a 404 error if no matching book has been found in the database
    if book.rowcount == 0:
        return jsonify({ "error": "This book doesn't exist"}),404

    # returning a JSON response if book was found
    return jsonify({
        "title": array[0],
        "author": array[1],          
        "year": array[2],
        "isbn": array[3],
        "review_count": array[4],
        "avg_score": float(array[5])
    })
    

#this route will destroy all the data in the session, logs the user off and redirects to the login page
@app.route("/logout")
def logout():
    session.pop('userID', None)
    session.pop('username', None)
    session.pop('password', None)
    return render_template("login.html")