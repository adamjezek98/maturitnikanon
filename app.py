# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory, render_template, request, redirect
import kanon
from operator import itemgetter
import os
import urllib.parse

app = Flask(__name__)


@app.route('/')
def books():
    k = kanon.Kanon()
    data = {}
    data["seasons"] = k.dbtool.get_books_by_seasons()
    return render_template("books.html", data=data)


@app.route('/31D98A545B3927780860a00183D8FE0F1/authors')
def authors():
    k = kanon.Kanon()
    data = {}
    data["authors"] = k.dbtool.get_authors()
    return render_template("authors.html", data=data)


@app.route('/31D98A545B3927780860a00183D8FE0F1/books')
def books_admin():
    k = kanon.Kanon()
    data = {"books": []}
    for s in k.dbtool.get_books_by_seasons(hide_none_authors=False):
        data["books"] += s["books"]
    data["books"] = sorted(data["books"], key=itemgetter('book_order'))
    data["authors"] = k.dbtool.get_authors()
    data["genres"] = k.get_genres()
    data["seasons"] = k.dbtool.get_seasons()
    return render_template("adminbooks.html", data=data)


@app.route('/api/<path:path>', methods=['POST'])
def api(path):
    k = kanon.Kanon()
    data = dict(request.form)
    if path == "modifyBook":
        return k.dbtool.modify_book(data)
    elif path == "deleteBook":
        return k.dbtool.delete_book(data)
    elif path == "addBook":
        return k.dbtool.add_book(data)
    if path == "modifyAuthor":
        return k.dbtool.modify_author(data)
    elif path == "deleteAuthor":
        return k.dbtool.delete_author(data)
    elif path == "addAuthor":
        return k.dbtool.add_author(data)
    elif path == "checkBooks":
        return k.check_books(data, request)
    return "NONE"


@app.route("/export", methods=["POST", "GET"])
def export():
    k = kanon.Kanon()
    docname = k.create_docx_file(request.form)
    print("exporting file", docname, end=" ")
    newdocname = urllib.parse.quote(docname)
    print("now", docname)
    return redirect("/exports/"+newdocname)
    return send_from_directory(directory=os.path.dirname(os.path.abspath(__file__)) + "/exports",
                               filename=docname, as_attachment=True, 
				mimetype="Content-Type: application/msword; charset=UTF8")


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5120)
