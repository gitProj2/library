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

    sql= """
        SELECT m.ID, p.NUMBER, p.title, p.date
        FROM LIBRARY.POST as p
        LEFT join LIBRARY.MEMBER as m
        on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
        """
    result = ""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        result += """<table>
                        <thead>
                            <tr>
                                <th>번호</th>
                                <th>제목</th>
                                <th>글쓴이</th>
                                <th>작성일시</th>
                            </tr>
                        </thead>
                    """
        for_rotation_counting = 0
        for (id, number, title, date) in cur:
            for_rotation_counting +=1
            result += """
                        <tr>
                            <th>{1}</th>
                            <th><a href="/community/watch_doc?p.number={4}">{2}</a></th> 
                            <th>{0}</th>
                            <th>{3}</th>
                        </tr>
                           
                        """.format(id, number, title, date, number)

        result += "</table>"
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/community/board_home.html", content = result, content1 = for_rotation_counting)

@app.route('/community/board_home_search', methods = ["GET"])
def search_doc():

    search_text_val = request.args.get("search_text")

    sql = """
        SELECT p.NUMBER, p.TITLE, m.ID, p.DATE 
        FROM LIBRARY.POST as p left join LIBRARY.MEMBER as m
        on m.NUMBER = p.MEMBER_NUMBER
        where p.TITLE LIKE '%{}%'
        order by p.NUMBER DESC;
        """.format(search_text_val)
    result = ""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        result += """
            <table>
                <thead>
                    <tr>
                        <th>번호</th>
                        <th>제목</th>
                        <th>글쓴이</th>
                        <th>작성일시</th>
                    </tr>
                </thead> """
    
        for_rotation_counting = 0
        for (number, title, id, date) in cur:
            for_rotation_counting +=1
            result += """
                    <tbody>
                        <tr>
                            <td>{0}</td>
                            <td><a href="/community/watch_doc?p.number={4}">{1}</a></td>
                            <td>{2}</td>
                            <td>{3}</td>
                        </tr>
                    </tbody>
                """.format(number, title, id, date, number)
        result += "</table>"
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template("/community/board_home_search.html", content = result, content1 = for_rotation_counting)
    

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

@app.route('/community/watch_doc', methods = ["GET"])
def watch_doc():
    post_number = request.args.get("p.number")
    result = ""
    try:
        sql = """
            SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
            p.MODIFY_DATE FROM LIBRARY.POST as p
            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
            WHERE p.NUMBER = {};
            """.format(post_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        for (title, contents, id, file, date, modify_date) in cur:
            if modify_date == None:
                modify_date = "수정 이력 없음"

                result += """
                        <h3>{0}</h3>
                        <div class="container">
                            <p>{1}</p>
                            <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                            
                            <input class="float-right" type="button" value="삭제">
                            <input class="float-right" type="button" value="수정">
                            <button class="float-right" disabled><span style="color: white;">작성자 :  {2} 작성일시 : {4} 최종 수정 : {5}</span></button>  
                        </div>
                        """.format(title, contents, id, file, date, modify_date)
            else:
                result += """
                        <h3>{0}</h3>
                        <div class="container">
                            <p>{1}</p>
                            <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                            
                            <input class="float-right" type="button" value="삭제">
                            <input class="float-right" type="button" value="수정">
                            <button class="float-right" disabled><span style="color: white;">작성자 :  {2} 작성일시 : {4} 최종 수정 : {5}</span></button>  
                        </div>
                        """.format(title, contents, id, file, date, modify_date)
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
            
    return render_template("/community/watch_doc.html", content_list= result)

    
@app.route('/community/write_doc')
def write_doc():
    author = session['id']
    return render_template("/community/write_doc.html", content = author)


# @app.route('/community/watch_doc')
# def add_comment():
#     author = session['id']
#     return render_template("/community/watch_doc.html", content = author)



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

