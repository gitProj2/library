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

    a_title = request.form["amend_title"]
    a_contents = request.form["contents"]
    a_post_file = request.form["file"]
    a_p_number = request.form["p_number"]


    if title and contents and post_file:
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

    elif a_title and a_contents and a_post_file and a_p_number:
        result = ""

        try:
            sql = """
                UPDATE LIBRARY.POST as p set TITLE ="{}", CONTENTS ="{}",
                POST_FILE ="{}", MODIFY_DATE = now()
                WHERE p.NUMBER = {};
                """.format(a_title, a_contents, a_post_file, a_p_number)

            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()

            sql1 = """
                    SELECT p.NUMBER, p.TITLE , p.CONTENTS, m.ID , p.DATE, p.MODIFY_DATE 
                    FROM LIBRARY.POST as p
                    left join LIBRARY.MEMBER as m
                    on p.MEMBER_NUMBER = m.NUMBER
                    where p.NUMBER ={};
                """.format(a_p_number)

            cur = conn.cursor()
            cur.execute(sql1)

            result = ""

            for (number, title, contents, id, date, modify_date) in cur:
                result += """
                            여기 작성                
                        
                        """
                





@app.route('/community/watch_doc', methods = ["GET"])
def watch_doc():
    post_number = request.args.get("p.number")


    result = ""
    try:
        sql = """
            SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
            p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
            WHERE p.NUMBER = {};
            """.format(post_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        for (title, contents, file, id, date, modify_date,p_number) in cur:
            if modify_date == None:
                modify_date = "수정 이력 없음"

                result += """
                        <h3>{0}</h3>
                        <div class="container">
                            <p>{1}</p>
                            <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                            
                            <input class="float-right" type="button" value="삭제">
                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                            <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>  
                        </div>
                        """.format(title, contents, file, id, date, modify_date, p_number)
            else:
                result +=  """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                            
                                <input class="float-right" type="button" value="삭제">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 :  {3} 작성일시 : {4} 최종 수정 : {5}</span></button>  
                            </div>
                        """.format(title, contents, file, id, date, modify_date, p_number)
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

@app.route('/community/amend_doc', methods = ['GET'])
def amend_doc():
    author = session['id']
    p_number = request.args.get("p_number")

    # tag = request.args.get("tag")
    # ajax = request.args.get("ajax")
    # if tag:
    #     ~~~
    # elif ajax:
    #     ~~~~
    #

    sql = """ 
        SELECT p.title, p.CONTENTS, p.post_file, p.NUMBER FROM LIBRARY.POST as p
        WHERE p.NUMBER = {};
        """.format(p_number)
    result = ""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        for (title, contents, file, p_number) in cur:
            result += """ 
                        <form action="/community/watch_doc" method="POST">
                            <div>
                                <p>제목 : </p>
                                <input tyle="text" value="{0}" name= "amend_title">
                            </div>
                            <br>
                            <textarea name="contents" value=>{1}</textarea>
                            <br>
                            <input type="hidden" name="p_number" value="{3}">
                            <div>
                                <p>파일첨부 :</p><input type="file" onclick="" name="file" value="{2}">
                                <input type="submit" value="저장" onclick="">
                            </div>
                        </form>
                    """.format(title, contents, file, p_number)
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/community/watch_doc_amend.html", content = author, content_amend = result)



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

