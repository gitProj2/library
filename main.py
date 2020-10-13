import mariadb
import sys

from flask import Flask, render_template, request

app = Flask(__name__)


def get_conn():
    conn = mariadb.connect(
        user="test",
        password="password",
        host="10.5.2.20",
        port=13306,
        database="LIBRARY"
    )
    return conn

@app.route('/')
def main():
    return render_template("/main.html")

@app.route('/sign_in')
def sign_in():
    return render_template("/sign_in.html")

@app.route('/sign_up')
def sign_up():
    return render_template("/sign_up.html")

@app.route('/member_info')
def member_info():
    return render_template("/member_info.html")

@app.route('/master/master')
def master():
    return render_template("/master/master.html")

@app.route('/community/board_home')
def board_home():
    return render_template("/community/board_home.html")

@app.route('/community/watch_doc')
def watch_doc():
    return render_template("/community/watch_doc.html")

@app.route('/community/write_doc')
def write_doc():
    return render_template("/community/write_doc.html")

@app.route("/books")
def books():
    sql = "SELECT NAME, IMG, LOAN FROM BOOK;"

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, IMG, LOAN) in cur:
            result += """
                <div class="book">
                    <input type="image" src="{1}" alt="책" width="100px" height="160px">
                    <span>{0}</span>
                    <span>{2}</span>
                </div>
                """.format(NAME, IMG, LOAN)

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/books.html", content=result)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

