# -*- coding: utf-8 -*-
import sqlite3
import config

config = config.Config()


class DbTool:
    def __init__(self):
        self.db = sqlite3.connect(config.dbpath)
        self.db.row_factory = sqlite3.Row
        self.c = self.db.cursor()

    def get_books_by_seasons(self, hide_none_authors=True):
        books = []
        self.c.execute("""SELECT * FROM book_seasons""")
        for book_season in self.c.fetchall():
            season = {}
            season["id"] = book_season["season_id"]
            season["name"] = book_season["season_name"]

            self.c.execute("SELECT * FROM books INNER JOIN authors ON authors.author_id = books.book_author  "
                           "WHERE book_season=? ORDER BY book_order", [season["id"]])
            season["books"] = []
            for book in self.c.fetchall():
                book = dict(book)
                book["typeText"] = self.get_type_text(book["book_genre"])
                if hide_none_authors and book["author_name"].lower().startswith("skryt"):
                    book["author_name"] = ""
                season["books"].append(book)
            books.append(season)

        return books

    def get_selected_books(self, books):
        print(books)
        self.c.execute("SELECT * FROM books INNER JOIN authors ON authors.author_id = books.book_author  "
                       "WHERE book_id IN (%s) ORDER BY book_order" % ','.join('?' * len(books)), books)
        b = []
        for i in self.c.fetchall():
            b.append(dict(i))
        print(len(b))
        return b

    def get_type_text(self, type):
        if type == 1:
            return "<span style='color: #148a14'>Próza</span>"
        if type == 2:
            return "<span style='color: #1b2ec5'>Poezie</span>"
        if type == 3:
            return "<span style='color: #865a15'>Drama</span>"

    def get_authors(self):
        self.c.execute("""SELECT * FROM authors ORDER BY author_name""")
        authors = []
        for a in self.c.fetchall():
            authors.append(dict(a))
        return authors

    def get_seasons(self):
        self.c.execute("""SELECT * FROM book_seasons""")
        seasons = []
        for s in self.c.fetchall():
            seasons.append(dict(s))
        return seasons

    def modify_book(self, data):
        try:
            self.c.execute("""UPDATE books 
                        SET book_order = ?, book_author = ?, book_name = ?, book_genre = ?, book_season = ? 
                        WHERE book_id = ?""",
                           [data["bookOrder"], data["bookAuthor"], data["bookName"],
                            data["bookGenre"], data["bookSeason"],
                            data["bookId"]])
            self.db.commit()

            return "OK"
        except Exception as e:
            return "Chyba: " + str(e)

    def delete_book(self, data):
        try:
            self.c.execute("""DELETE FROM books  WHERE book_id = ?""",
                           [data["bookId"], ])
            self.db.commit()
            return "OK"
        except Exception as e:
            return "Chyba: " + str(e)

    def add_book(self, data):
        # try:
        self.c.execute("""SELECT author_id FROM authors ORDER BY author_name LIMIT 1""")
        firstauthor = self.c.fetchall()[0]["author_id"]
        self.c.execute("""SELECT book_order fROM books ORDER BY book_order DESC LIMIT 1""")
        booksCount = self.c.fetchall()[0][0]
        for i in range(int(data["count"])):
            self.c.execute("""INSERT INTO books (book_season, book_genre, book_author, book_order, book_name)
                          VALUES (1, 1, ?, ?, "===NOVÁ KNIHA===")""",
                           [firstauthor, booksCount + 1 + i])
        self.db.commit()
        return "OK"
        # except Exception as e:
        #    return "Chyba: " + str(e)

    def modify_author(self, data):
        try:
            self.c.execute("""UPDATE authors 
                            SET author_name = ?
                            WHERE author_id = ?""",
                           [data["authorName"], data["authorId"]])
            self.db.commit()
            return "OK"
        except Exception as e:
            return "Chyba: " + str(e)

    def delete_author(self, data):
        try:
            self.c.execute("""DELETE FROM authors  WHERE author_id = ?""",
                           [data["authorId"], ])
            self.db.commit()
            return "OK"
        except Exception as e:
            return "Chyba: " + str(e)

    def add_author(self, data):
        # try:
        self.c.execute("""INSERT INTO authors (author_name) VALUES ("==NOVÝ AUTOR==")""")
        self.db.commit()
        return "OK"
        # except Exception as e:
        #    return "Chyba: " + str(e)
