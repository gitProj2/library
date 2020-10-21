import mariadb
import sys
from flask import Flask, render_template, request, session

app = Flask(__name__)

# Oracle Cloud MariaDB Connect
def get_conn():
    conn = mariadb.connect(
        user="root",
        password="password",
        host="193.122.100.83",
        port=13306,
        database="LIBRARY"
    )
    return conn

@app.route('/')
def main():
    session.clear()
    session['id'] = "wonjun7"
    session['number'] = 1
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
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   books 페이지 aside 카테고리 목록 및 책 목록 조회                                   #
    ###################################################################################

    # catagory_number - 좌측 C, Java 등의 책 카테고리의 DB의 number값
    # title - 책 제목 검색
    # session[number] - login 후 session에 보관하는 회원정보의 number 값(PK)
    catagory_number = request.args.get("catagory_number")
    title = request.args.get("title")
    number = session["number"]

    try:
        ############################################################################################################
        # 책 카테고리 목록 조회 및 구성                                                                                #
        sql = "SELECT NUMBER, NAME FROM CATAGORY_BOOK ORDER BY NUMBER "

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        aside = """
            <li><h4><a href="/books">전체보기</a></h4></li>"""

        for (NUMBER, NAME) in cur:
            aside += """
            <li><a href="/books?catagory_number='{0}'">{1}</a></li>""".format(NUMBER, NAME)
        #                                                                                                          #
        ############################################################################################################

        ############################################################################################################
        # 책 목록 조회 및 구성                                                                                        #
        sql = """
        SELECT B.NUMBER, B.NAME, B.IMG, B.LOAN, R.MEMBER_NUMBER FROM RENTER_RECORD R
        JOIN BOOK B
        ON B.NUMBER = R.BOOK_NUMBER 
        AND R.LOAN = 'N'"""

        sql2 = """
        UNION ALL
        SELECT B.NUMBER, B.NAME, B.IMG, B.LOAN ,0 AS MEMBER_NUMBER FROM BOOK B 
        WHERE LOAN != 'N'
        """

        if catagory_number is not None:
            sql += "AND CATAGORY_NUMBER = "
            sql += catagory_number + " "
            sql2 += "AND CATAGORY_NUMBER = "
            sql2 += catagory_number + " "

        if title is not None:
            sql += "AND NAME LIKE '%{0}%' ".format(title)
            sql2 += "AND NAME LIKE '%{0}%' ".format(title)


        sql2 += "ORDER BY NUMBER ASC "
        sql += sql2

        cur = conn.cursor()
        cur.execute(sql)
        result = ""

        for (NUMBER, NAME, IMG, LOAN, MEMBER_NUMBER) in cur:
            result += """
                <div class="book" id="book_{0}">
                    <input type="image" src="{2}" alt="책" width="100px" height="160px">
                    <span>{1}</span>""".format(NUMBER, NAME, IMG)
            if MEMBER_NUMBER == number:
                if LOAN != 'Y':
                    result += """
                        <button type="button" id="book_borrow_{0}" onclick="return_book('{0}',this)">반납</button>
                    </div>""".format(NUMBER)
            else :
                if LOAN == 'Y':
                    result += """
                        <button type="button" id="book_borrow_{0}" onclick="borrow_book('{0}',this)">대여</button>
                    </div>""".format(NUMBER)
                else:
                    result += """
                        <span id="book_borrow_{0}">대여 중</span>
                    </div>""".format(NUMBER)
    ################################################################################################################

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/books.html", tag=aside, content=result)

@app.route("/book_borrow")
def book_borrow():
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   책 대여 ajax 기능                                                              #
    ###################################################################################

    # session["id"] - login 후 session에 보관하는 회원정보의 id 값
    # request.args.get("book_number") - 대여처리 해야하는 book의 테이블 number 값(PK)
    id = session["id"]
    book_number = request.args.get("book_number")

    try:
        ####################################################################################
        # 대여기록 테이블에 대여기록 INSERT
        sql = "INSERT INTO RENTER_RECORD (MEMBER_NUMBER, BOOK_NUMBER, DATE, RETURN_DATE, LOAN) VALUES((SELECT NUMBER FROM MEMBER WHERE ID='{0}'), {1}, NOW(), NULL, 'N')".format(id, book_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        ####################################################################################

        ####################################################################################
        # 책 테이블에 대여여부 컬럼 UPDATE
        sql = "UPDATE BOOK SET LOAN = 'N' WHERE NUMBER = {0}".format(book_number)

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return "대여 성공!"

@app.route("/book_return")
def return_book():
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   책 반납 ajax 기능                                                              #
    ###################################################################################

    # session["id"] - login 후 session에 보관하는 회원정보의 id 값
    # session["number"] - login 후 session에 보관하는 회원정보의 number 값
    # request.args.get("book_number") - 대여처리 해야하는 book의 테이블 number 값(PK)
    id = session["id"]
    number = session["number"]
    book_number = request.args.get("book_number")

    try:
        ####################################################################################
        # 대여기록 테이블에 대여기록 (반납시간 = NULL -> 현재 연월일, 반납여부 = N -> Y ) UPDATE
        sql = "UPDATE BOOK SET LOAN = 'Y' WHERE NUMBER = {0}".format(book_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        sql = "UPDATE RENTER_RECORD SET LOAN = 'Y', RETURN_DATE = NOW() WHERE MEMBER_NUMBER = {0} AND BOOK_NUMBER = {1} ".format(number, book_number)

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        ####################################################################################

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return "반납 성공!!"


if __name__ == "__main__":
    app.secret_key = 'app secret key'
    app.run(host='0.0.0.0')

