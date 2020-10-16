import mariadb
import sys
from flask import Flask, render_template, request, session

app = Flask(__name__)


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
    session['id'] = "nywogud"
    session['number'] = 3
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
## 글 작성 버튼 클릭하면 회원여부 확인 후 글 작성 페이지로 이동, 회원이 아니면 경고 메시지 띄우기
def board_home():

    sql1 = "SELECT ID FROM LIBRARY.`MEMBER` where `NUMBER` ;"
    #아이디 호출

    # SELECT m.NUMBER, m.ID, p.title, p.date, p.modify_date, p.post_file, p.contents 
    # FROM LIBRARY.POST as p
    # LEFT join LIBRARY.MEMBER as m
    # on p.MEMBER_NUMBER = m.NUMBER;


    sql2 = "SELECT `NUMBER` , TITLE, `DATE`, MODIFY_DATE from LIBRARY.POST;"
    #글 번호, 제목, 작성일, 최종수정일 호출

    try:
        conn1 = get_conn()
        cur1 = conn1.cursor()
        cur1.execute(sql1)
        # cur1은 아이디 값

        conn2 = get_conn()
        cur2 = conn2.cursor()
        cur2.execute(sql2)
        # cur2는 글 번호, 제목, 작성일, 최종수정일 값

        cur1 = id


        result = ""
        result += """<table>
                        <thead>
                            <tr>
                                <th>글 번호</th>
                                <th>제목</th>
                                <th>작성자</th>
                                <th>작성일</th>
                                <th>최종수정</th>
                            </tr>
                        </thead>
                    """

    except:
        pass

    return render_template("/community/board_home.html")

@app.route('/community/write_doc')
def write_doc():
    author = session['id']
    return render_template("/community/write_doc.html", content = author)

@app.route('/community/watch_doc')
def watch_doc():
    return render_template("/community/watch_doc.html")

@app.route('/community/watch_doc', methods = ["POST"])
def send_doc():
    title = request.form["title"]
    contents = request.form["contents"]
    post_file = request.form["post_file"]
    result = ""

    try:
        sql  = "INSERT into LIBRARY.POST (TITLE, MEMBER_NUMBER, POST_FILE, CONTENTS, `DATE`, VIEW) values ('{}',{},'{}','{}', now(), 0);".format(title, session['number'], post_file, contents )
        # 조회한 회원 id 값과 form으로 받은 값들을 db에 전송한다.

        
        conn = get_conn()
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

    return render_template("/community/watch_doc.html")


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
    app.secret_key = 'app secret key'
    app.run(host='0.0.0.0')

