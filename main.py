import mariadb
import sys, datetime, os
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
    
    return render_template("/main.html")

#로그인 화면
@app.route('/sign_in')
def sign_in():
    return render_template("/sign_in.html")

#로그인 화면에서 입력한 ID와 PW 체크 (DB에 있는지 여부 확인)
@app.route('/sign_in', methods=['POST'])
def check_id():
    insert_id = request.form['id']
    insert_pw = request.form['pw']
    login_flag = False

    result =""

    sql = "SELECT ID, PW, NUMBER FROM MEMBER WHERE ID = '{}'".format(insert_id)
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        for (ID, PW, NUMBER) in cur:
            result = "{0},{1}".format(ID,PW)

            # 입력한 ID와 PW가 DB와 일치하는 경우
            if ID == insert_id and PW == insert_pw :
                session.clear()
                session['id'] = request.form['id']
                session['number'] = NUMBER
                login_flag = True
                break

    except mariadb.Error as e:
        print("ERR: {}".format(e))
        sys.exit(1)
    except TypeError as e:
        result = ""
    if conn:
        conn.close()
        # 입력한 ID나 PW 둘 중 하나라도 DB와 일치하지 않은 경우
        result = """
        <script>
        alert("아이디 또는 패스워드를 확인 하세요.");
        </script>
        """
    if login_flag: return render_template('/main.html')
    else: return render_template('/sign_in.html', content=result)

#회원가입화면
@app.route('/sign_up')
def sign_up():
    return render_template("/sign_up.html")

#회원가입 정보를 DB 입력
@app.route('/sign_up', methods=['POST'])
def member_info_insert():
    new_id = request.form["id"]
    new_pw = request.form["pw"]
    new_name = request.form["name"]
    new_gender = request.form["gender"]
    new_birthday = request.form["birthday"]
    new_phone = request.form["phone"]
    new_email = request.form["email"]

    try:
        conn = get_conn()
        cur = conn.cursor()
        sql = "INSERT INTO MEMBER(id, pw, name, gender, birthday, phone, email) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(new_id, new_pw, new_name, new_gender, new_birthday, new_phone, new_email)
        print(sql)
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template('/main.html')

# 로그인 한 경우 회원정보 불러오기
@app.route('/member_info')
def member_info():
    result = ""

    # 로그인 한 값이 있는 경우 DB에서 해당 정보를 불러오고, 없는 경우 로그인 알림창 뜸.
    if 'number' in session:
        r_num = session['number']
    else:
        result = """
        <script>
        alert("먼저 로그인 하세요.");
        </script>
        """
        return render_template("/main.html", content=result)

    sql = "SELECT NUMBER, ID, PW, PHONE, EMAIL, GENDER, NAME, BIRTHDAY FROM MEMBER WHERE NUMBER = {}".format(r_num)

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        
        result = ""
        for (ID, PW, NAME, GENDER, BIRTHDAY, PHONE, EMAIL, NUMBER) in cur:
            # < input type = "hidden" value = "{0}" >

            result = """      
            <article>
            <div>            
            <ul class=\"box1\">
                <li>아이디 &emsp;&emsp;<input type="text" name="id" readonly text-align="left" height="40" value="{1}" class="input_box"></li>
                <li>비밀번호 &emsp;<input type="password" name="pw" text-align="left" height="40" value="{2}" class="input_box"></li>
            </ul>
            &nbsp;
        </div>
        <div>
            <ul class=\"box2\">
                <li>이름 &emsp;&emsp;&emsp;<input type="text" name="name" height="40" value="{6}" class="input_box" ></li>
                <li>성별 &emsp;&emsp;&emsp;<input type="text" name="gender" height="40" value="{5}" class="input_box" ></li>
                <li>생년월일 &emsp;<input type="text" name="birthday" height="40" value="{7}" class="input_box" ></li>
                <li>연락처 &emsp;&emsp;<input type="text" name="phone" height="40" value="{3}" class="input_box"></li>
                <li>이메일 &emsp;&emsp;<input type="text" name="email" height="40" value="{4}" class="input_box"></li>
            </ul>
        </div>""".format(ID, PW, NAME, GENDER, BIRTHDAY, PHONE, EMAIL, NUMBER)

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/member_info.html", content=result)

# 만일 불러온 회원정보에서 수정사항이 있는 경우 수정된 회원정보 DB입력 / ID는 수정불가
@app.route('/member_info', methods=['POST'])
def member_info_modify():
    id = request.form["id"]
    pw = request.form["pw"]
    name = request.form["name"]
    gender = request.form["gender"]
    birth= request.form["birthday"]
    phone = request.form["phone"]
    email = request.form["email"]
    sql = "UPDATE MEMBER SET pw='{0}',name='{1}',gender='{2}',birthday='{3}',phone='{4}',email='{5}' WHERE id='{6}'".format(
        pw, name, gender, birth, phone, email, id)

    print(sql)

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        print(e)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/main.html")

@app.route('/game') # 가볍게 즐기는 가위바위보 게임
def game():
    return render_template("/game/game.html")

@app.route('/master/master')
def master_m():
    c_del = request.args.get("delete")
    # delete , None
    conn = get_conn()
    if c_del is not None:
        cur = conn.cursor()
        cur.execute("UPDATE LIBRARY.`MEMBER` SET ID='unknown', PW=1234, PHONE=NULL, EMAIL=NULL, GENDER=NULL, NAME=NULL, BIRTHDAY=NULL WHERE `ID`='{}';".format(c_del))
        conn.commit()

    result = ""
    # 로그인 한 값이 있는 경우 DB에서 해당 정보를 불러오고, 없는 경우 로그인 알림창 뜸.
    if 'number' in session:
        r_num = session['number']
        print(r_num)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result)

    if r_num == 1: # 마스터계정 번호일경우 접속
        print(1)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result) 


    sql = "select NAME, ID, PHONE, EMAIL from MEMBER where ID not in('unknown');"
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, ID, PHONE, EMAIL) in cur:
            
            result += """
                <tbody>
                    <tr>
                        <td>{1}</td>
                        <td>{0}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                <tbody>
                """.format(NAME, ID, PHONE, EMAIL)
    except mariadb.Error as e:
        print(e)
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/master.html", content=result)


@app.route('/master/community')
def master_c():
    c_del = request.args.get("delete")
    # delete , None
    conn = get_conn()
    if c_del is not None:
        cur = conn.cursor()
        cur.execute("DELETE FROM POST WHERE NUMBER IN ({})".format(c_del))
        conn.commit()

    sql = """
        SELECT m.ID, p.NUMBER, p.title, p.date
        FROM LIBRARY.POST as p
        LEFT join LIBRARY.MEMBER as m
        on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
        """
    result = ""

    try:
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
            for_rotation_counting += 1
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

    return render_template("/master/community.html", content=result, content1=for_rotation_counting)


@app.route('/master/books', methods=['GET','POST'])
def master_b():
    try:
        conn = get_conn()
        if request.method == 'GET':
            c_del = request.args.get("delete")
            # delete , None    
            if c_del is not None:
                cur = conn.cursor()
                cur.execute("DELETE FROM BOOK WHERE NUMBER IN ({})".format(c_del))
                conn.commit()        
        else:
            book_name = request.form["book_name"]
            book_contents = request.form["book_contents"]
            book_catagory = request.form["book_catagory"]
            file = request.files['book_file']

            sql = """
            INSERT INTO LIBRARY.BOOK 
            (NAME, CONTENTS, CATAGORY_NUMBER, IMG, LOAN) 
            VALUES(
            '{0}',
            '{1}', 
            (SELECT `NUMBER` FROM CATAGORY_BOOK WHERE NAME = '{2}'), 
            '/static/image/books/{3}', 
            'Y'
            )""".format(book_name, book_contents, book_catagory, file.filename)

            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()

            file.save(os.path.join('./static/image/books', file.filename))


        sql = "SELECT NAME, IMG, LOAN, CONTENTS, NUMBER FROM BOOK;"

        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, IMG, LOAN, CONTENTS, NUMBER) in cur:
            result += """
                <div class="book">
                    <input type="image" src="{1}" alt="책" width="100px" height="160px" style="margin-right:15px;">
                    <span id="exa" style="font-size:16px;">{3}</span><br><br>
                    <span style="font-size:18px; color:blue; font-weight: bold;">{0} (책번호 : {4})</span>
                    <span style=font-size:25px;> / <span>
                    <span style="font-size:18px; color:green; font-weight: bold;">대여여부 : </span>
                    <span style=color:red;>{2}</span>
                    <br><br><br>
                </div>
                """.format(NAME, IMG, LOAN, CONTENTS, NUMBER)
        
        sql = "SELECT NUMBER, NAME FROM CATAGORY_BOOK ORDER BY NUMBER "
        cur = conn.cursor()
        cur.execute(sql)

        modal_book_catagory = ""
        for (NUMBER, NAME) in cur:
            modal_book_catagory += """
            <option value="{1}">{1}</option>""".format(NUMBER, NAME)

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/books.html", content=result, catagory_tag=modal_book_catagory)

@app.route('/community/board_home')
## 글 작성 버튼 클릭하면 회원여부 확인 후 글 작성 페이지로 이동, 회원이 아니면 경고 메시지 띄우기- 기능 구현 전
def board_home():
# 데이터베이스에서 아래 값들을 불러와 보드홈에서 내림차순 테이블 구현
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
        for_rotation_counting = 0 # for 문이 회전하는 횟수를 계산해 게시글 수 확인 후 변수에 담아 테이블과 함께 게시판 html에 전달
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
            # 글 제목에 링크를 걸어 해당 글을 화면 이동

        result += "</table>"
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


    return render_template("/community/board_home.html", content=result, content1=for_rotation_counting)

@app.route('/community/board_home_search', methods = ["GET"]) # 게시판 홈에서 검색어를 GET방식으로 전달 받아 DB에서 값 수신
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
    #DB에서 가져온 값을 자동 생성 표에 넣고 이를 담은 변수와 for문의 회전 횟수를 담은 변수를 함께 위 경로에 렌더링

@app.route('/community/watch_doc', methods = ["GET"])
#게시판 홈에서 사용자가 클릭한 글 제목을 GET 방식으로 watch_doc에서 전달 받아 DB 연산 진행
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

    return render_template("/community/watch_doc.html", content= result)
    #연산한 결과를 watch_doc.html에서 전달 받아 이를 출력


@app.route('/community/write_doc')#사용자가 글 작성 메뉴를 클릭하면 이동되는 화면
def write_doc():
    author = session['id']
    return render_template("/community/write_doc.html", author = author)


# @app.route('/community/watch_doc')
# def add_comment():
#     author = session['id']
#     return render_template("/community/watch_doc.html", author = author)

@app.route('/community/amend_doc', methods = ['GET'])
# 사용자가 수정을 클릭하면 실행되는 함수, 글 번호를 GET방식으로 전달받는다.
def amend_doc():
    author = session['id']
    p_number = request.args.get("p_number")

    # 해당 경로에서 각기 다른 인자값을 전달 받아 DB 연산을 수행하는 용례

    # tag = request.args.get("tag")
    # ajax = request.args.get("ajax")
    # if tag:
    #     ~~~
    # elif ajax:
    #     ~~~~

    sql = """ 
        SELECT p.title, p.CONTENTS, p.post_file, p.NUMBER FROM LIBRARY.POST as p
        WHERE p.NUMBER = {};
        """.format(p_number)
    result = ""
    #수정에 필요한 모든 값들을 쿼리문으로 불러옴.
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)


        for (title, contents, file, p_number) in cur:
            result += """ 
                        <form action="/community/watch_doc?amend_p_number={3}" method="POST">
                            <p>제목 : </p>
                            <input type="text" value="{0}" name= "amend_title">
                            <br>
                            <textarea name="amend_contents">{1}</textarea>
                            <br>
                            <div>
                                <p>파일첨부 :</p><input type="file" onclick="" name="amend_file" value="{2}">
                                <input type="submit" value="저장" onclick="">
                            </div>
                        </form>
                    """.format(title, contents, file, p_number)
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/community/watch_doc_amend.html", author = author, content_amend = result)
    #실행결과를 watch_doc_amend.html에 변수에 담아 전달


@app.route('/books')
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

@app.route('/book_borrow')
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

@app.route('/book_return')
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

