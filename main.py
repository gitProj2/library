import mariadb
import sys, datetime
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
    # session['id'] = 'nywogud'
    # session['number'] = 3

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


@app.route('/master/master')
def master_m():
    sql = "SELECT NAME, ID, PHONE, EMAIL FROM MEMBER;"

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, ID, PHONE, EMAIL) in cur:
            result += """
                <tbody>
                    <tr>
                        <td>{0}</td>
                        <td>{1}</td>
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
    sql = """
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


@app.route('/master/books')
def master_b():
    sql = "SELECT NAME, IMG, LOAN, CONTENTS FROM BOOK;"

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, IMG, LOAN, CONTENTS) in cur:
            result += """
                <div class="book">
                    <input type="image" src="{1}" alt="책" width="100px" height="160px" style="margin-right:15px;">
                    <span style="font-size:22px; position:absolute;">{3}</span><br>
                    <span style="font-size:18px; color:blue;">{0}</span>
                    <span style=font-size:25px;> / <span>
                    <span style=font-size:18px;>대여여부 : </span>
                    <span style=color:red;>{2}</span><br><br><br>
                </div>
                """.format(NAME, IMG, LOAN, CONTENTS)
    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/books.html", content=result)

# 데이터베이스에서 아래 값들을 불러와 보드홈에서 내림차순 테이블 구현
@app.route('/community/board_home')
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

# 게시판 홈에서 검색어를 GET방식으로 전달 받아 DB에서 값 수신
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
    #DB에서 가져온 값을 자동 생성 표에 넣고 이를 담은 변수와 for문의 회전 횟수를 담은 변수를 함께 위 경로에 렌더링


#사용자가 글을 작성한 후 혹은 본인 글을 수정한 후 넘어오는 함수. 내용을  POST로 받아 온다. 중복 확인할 필요는 없지만 로그인 세션을 한번 더 확인한다.
@app.route('/community/watch_doc', methods = ["POST"])
def send_show_doc():

    if 'id' in session:

        try:
            title = request.form["title"]
            contents = request.form["contents"]
            post_file = request.form["post_file"] # request.files

            if title == '':
                alert = """
                        <script>
                            alert("제목을 작성하세요.")
                        </script>
                        """
                return render_template('/main.html', alert=alert)

            else:

                try:
                    sql = """
                        SELECT 1 FROM LIBRARY.POST as p
                        left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                        WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                    """.format(title, contents, session['id'])

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    check_duple = ()
                    for check_duple in cur:
                        break
                    print(check_duple)
                    # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                    if check_duple ==(1,):
                        result = """
                        <script>
                            alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                        </script>
                        """
                        return render_template('/main.html', alert = result)

                    else:
                        sql  = "INSERT into LIBRARY.POST (TITLE, MEMBER_NUMBER, POST_FILE, CONTENTS, `DATE`, VIEW) values ('{}',{},'{}','{}', now(), 0);".format(title, session['number'], post_file, contents )
                        # 조회한 회원 id 값과 form으로 받은 값들을 db에 전송한다.


                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)
                        conn.commit()

                        sql = """
                                SELECT p.NUMBER FROM LIBRARY.POST as p
                                where p.MEMBER_NUMBER = {} AND p.TITLE = '{}';
                                """.format(session['number'], title)
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        g = ()
                        for g in cur:
                            break
                        p_number = g[0]

                        # remeber_p_number()에 p_number를 저장
                        check_p_number.insert_p_number(p_number)

                        sql = """ 
                                SELECT p.TITLE, p.CONTENTS, m.ID , p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                                from LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m
                                on p.MEMBER_NUMBER = m.NUMBER 
                                WHERE  p.NUMBER IN (SELECT p.number FROM LIBRARY.POST as p where p.TITLE = '{}' and p.CONTENTS = '{}');
                            """.format(title, contents)
                        cur = conn.cursor()
                        cur.execute(sql)

                        result = ""
                        for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                            modify_date = "수정이력 없음"
                            result +="""
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, id, post_file, date, modify_date, p_number)
                        no_com = 0

                except mariadb.Error as e:
                    print(e)

                except mariadb.Error as e:
                    print(e)
                    sys.exit(1)

                finally:
                    if conn:
                        conn.close()

                return render_template("/community/watch_doc.html", content= result, no_com = no_com)

        #사용자가 수정한 게시글에서 기존 댓글을 출력
        except:

            amend_title = request.form["amend_title"]
            amend_contents = request.form["amend_contents"]
            amend_post_file = request.form["amend_file"]
            amend_post_number = request.form["amend_p_number"]

            print(amend_title)
            print(type(amend_title))

            try:
            # 왜 안될까.....
            #     if bool(amend_title) == False:
            #         alert = """
            #                 <script>
            #                     alert("제목을 작성하세요.")
            #                 </script>
            #                 """
            #         return render_template('/main.html', alert=alert)
            #     else:
                    # remeber_p_number()에 amend_post_number를 저장
                    check_p_number.insert_p_number(amend_post_number)

                    sql = """
                            SELECT 1 FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                            WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                        """.format(amend_title, amend_contents, session['id'])

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    check_duple = ()
                    for check_duple in cur:
                        break
                    # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                    if check_duple == (1,):
                        result = """
                                <script>
                                    alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                                </script>
                                """
                        return render_template('/main.html', alert=result)
                    else:
                        sql = """
                            UPDATE LIBRARY.POST as p set TITLE ="{0}", CONTENTS ="{1}",
                            POST_FILE ="{2}", MODIFY_DATE = now()
                            WHERE p.NUMBER = {3};
                            """.format(amend_title, amend_contents, amend_post_file, amend_post_number)

                        cur = conn.cursor()
                        cur.execute(sql)
                        conn.commit()

                        sql = """
                                SELECT p.TITLE , p.CONTENTS, m.ID ,p.post_file, p.DATE, p.MODIFY_DATE, p.number
                                FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m
                                on p.MEMBER_NUMBER = m.NUMBER
                                where p.NUMBER ={};
                            """.format(amend_post_number)

                        cur = conn.cursor()
                        cur.execute(sql)
                        result = ""
                        for (title, contents, id, file, date, modify_date, number) in cur:
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, id, file, date, modify_date, number)

                        # 댓글 조회 후 자동 내림차순 정렬
                        sql = """
                                SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                                from LIBRARY.COMMENT 
                                where POST_NUMBER = {};
                            """.format(amend_post_number)
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        comment_result = ""
                        comment_for_rotation_counting = 0
                        for (comment, id, date, c_modify_date, c_number) in cur:
                            comment_for_rotation_counting += 1
                            comment_result += """
                                                <div class="container">
                                                    <p>{0}</p>
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                    <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                    <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                                </div>
                                                <script>
                                                    function com_delete_check_btn_{4}(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_com?del_c_number={4}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                            """.format(comment, id, date, c_modify_date, c_number)

            except mariadb.Error as e:
                print(e)

            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            finally:
                if conn:
                    conn.close()

            return render_template("/community/watch_doc.html", content= result, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)

@app.route('/community/watch_doc', methods = ["GET"])
def watch_doc():
    post_number_temp_bang = request.args.get("p.number")
    # remeber_p_number()에 p.number를 저장
    check_p_number.insert_p_number(post_number_temp_bang)

    result = ""
    try:
        sql = """
            SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
            p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
            WHERE p.NUMBER = {};
            """.format(post_number_temp_bang)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)



        for (title, contents, file, id, date, modify_date,p_number) in cur:
            if modify_date == None:
                modify_date = "수정 내역 없음"

                result += """
                        <h3>{0}</h3>
                        <div class="container">
                            <p>{1}</p>
                            <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                            <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                        </div>
                        <script>
                            function delete_check_btn(){{
                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                window.location = '/community/delete_doc?p_number={6}';
                              }} else{{
                                return false;
                              }}
                           }}
                        </script>
                        """.format(title, contents, file, id, date, modify_date, p_number)
            else:
                result += """
                            <h3>{0}</h3>
                        <div class="container">
                            <p>{1}</p>
                            <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                            <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                        </div>
                        <script>
                            function delete_check_btn(){{
                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                window.location = '/community/delete_doc?p_number={6}';
                              }} else{{
                                return false;
                              }}
                           }}
                        </script>
                        """.format(title, contents, file, id, date, modify_date, p_number)


        sql = """
                SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                from LIBRARY.COMMENT 
                where POST_NUMBER = {};
            """.format(post_number_temp_bang)

        cur = conn.cursor()
        cur.execute(sql)

        comment_result = ""
        comment_for_rotation_counting = 0
        for (comment, id, date, c_modify_date, c_number) in cur:
            comment_for_rotation_counting += 1
            comment_result += """
                            <div class="container">
                                <p>{0}</p>
                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                            </div>
                            <script>
                                function com_delete_check_btn_{4}(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_com?del_c_number={4}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                        """.format(comment, id, date, c_modify_date, c_number)

    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/community/watch_doc.html", content= result, com_content = comment_result, for_rotation_counting = comment_for_rotation_counting)
    #연산한 결과를 watch_doc.html에서 전달 받아 이를 출력


@app.route('/community/write_doc')#사용자가 글 작성 메뉴를 클릭하면 이동되는 화면
def write_doc():
    author = session['id']
    return render_template("/community/write_doc.html", author = author)

@app.route('/community/amend_doc', methods = ['GET'])
# 사용자가 게시글에 수정 버튼을 클릭하면 실행되는 함수, 글 번호를 GET방식으로 전달받는다.
def amend_doc():
    p_number = request.args.get("p_number")
    if 'id' in session:

        sql = """
            SELECT m.ID from LIBRARY.POST as p
            left join LIBRARY.MEMBER as m
            on p.MEMBER_NUMBER = m.NUMBER 
            WHERE  p.NUMBER = '{}';
            """.format(p_number)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        for data in cur:
            break

        if data[0] == session['id']:

            sql = """ 
                    SELECT p.title, p.CONTENTS, p.post_file, p.NUMBER FROM LIBRARY.POST as p
                    WHERE p.NUMBER = {};
                    """.format(p_number)
            result = ""
            # 수정에 필요한 모든 값들을 쿼리문으로 불러옴.
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, p_number) in cur:
                    result += """ 
                            <form action="/community/watch_doc" method="POST">
                                <p>제목</p>
                                <br>
                                <input type="text" name= "amend_title" value="{0}">
                                <br>
                                <textarea rows="30" style="width: 100%; resize: none;" name="amend_contents">{1}</textarea>
                                <input type="hidden" name="amend_p_number" value="{3}">
                                <br>
                                <div>
                                    <p>파일첨부 :</p><input type="file" onclick="" name="amend_file">
                                    <input style ="float:right" type="submit" value="저장" onclick="">
                                </div>
                            </form>
                                """.format(title, contents, file, p_number)

            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template("/community/watch_doc_amend.html", content_amend=result)
            # 실행결과를 watch_doc_amend.html에 변수에 담아 전달

        # 로그인한 사용자가 해당 글을 작성하지 않은 경우
        else:
            alert = """
                <script>
                    alert("수정 권한이 없습니다.")
                </script>
            """

            sql = """
                SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER
                FROM LIBRARY.POST as p
                left join LIBRARY.MEMBER as m
                on p.MEMBER_NUMBER = m.NUMBER
                where p.NUMBER ={};
                """.format(p_number)
            result = ""

            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                result = ""
                for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "수정이력 없음"
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, id, post_file, date, modify_date, p_number)
                    else:
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, id, post_file, date, modify_date,
                                           p_number)

            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template('/community/watch_doc.html', content =result, alert=alert)

    # 로그인 하지 않고 수정 버튼 누른 경우
    else:
        alert = """
                <script>
                    alert("수정 권한이 없습니다.")
                </script>
                """
        sql = """
            SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE ,p.NUMBER
            FROM LIBRARY.POST as p
            left join LIBRARY.MEMBER as m
            on p.MEMBER_NUMBER = m.NUMBER
            where p.NUMBER ={};
            """.format(p_number)
        result = ""

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)

            result = ""
            for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                if modify_date == None:
                    modify_date = "수정이력 없음"
                    result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, id, post_file, date, modify_date, p_number)
                else:
                    result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, id, post_file, date, modify_date, p_number)

        except mariadb.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

        return render_template('/community/watch_doc.html', content=result, alert = alert)

# 사용자가 게시글 삭제 버튼을 누르고 alert 창에서 확인 버튼을 누르면 넘어오는 함수. GET방식으로 p_number 값이 함께 넘어온다.
@app.route('/community/delete_doc', methods = ["GET"])
def delete_query():
    p_number = request.args.get("p_number")
    if 'id' in session:

        sql = """
            SELECT m.ID from LIBRARY.POST as p
            left join LIBRARY.MEMBER as m
            on p.MEMBER_NUMBER = m.NUMBER 
            WHERE  p.NUMBER = '{}';
            """.format(p_number)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        #data = ()
        for data in cur:
            break

        if data[0] == session['id']:
            try:
                try:
                    sql = """
                        DELETE FROM LIBRARY.POST where NUMBER = {} ;
                       """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                except:
                    sql = """
                        SELECT c.COMMENT_NUMBER FROM LIBRARY.COMMENT as c
                        where c.POST_NUMBER = {};
                    """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    d_progresss = ()
                    for d_progresss in cur:
                        print(d_progresss)

                    for u in range(len(d_progresss)):
                        sql = ""
                        sql = """
                            DELETE FROM LIBRARY.COMMENT
                            where COMMENT_NUMBER ={};
                        """.format(int(d_progresss[u]))

                        cur = conn.cursor()
                        cur.execute(sql)

                    sql = """
                        DELETE FROM LIBRARY.POST
                        where `NUMBER` = {};
                        """.format(p_number)
                    cur = conn.cursor()
                    cur.execute(sql)

                sql = """
                        SELECT m.ID, p.NUMBER, p.title, p.date
                        FROM LIBRARY.POST as p
                        LEFT join LIBRARY.MEMBER as m
                        on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
                        """
                result = ""

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
                for_rotation_counting = 0  # for 문이 회전하는 횟수를 계산해 게시글 수 확인 후 변수에 담아 테이블과 함께 게시판 html에 전달
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
                    # 글 제목에 링크를 걸어 해당 글을 화면 이동

                result += "</table>"

            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template("/community/board_home.html", content=result, content1=for_rotation_counting)
        # 로그인한 사용자가 다른 사용자의 글을 삭제하려는 경우
        else:
            alert = """
                    <script>
                        alert("삭제 권한이 없습니다.")
                    </script>
                """

            sql = """
                SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                FROM LIBRARY.POST as p
                left join LIBRARY.MEMBER as m
                on p.MEMBER_NUMBER = m.NUMBER
                where p.NUMBER ={};
                """.format(p_number)
            result = ""

            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                result = ""
                for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "수정이력 없음"
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, id, post_file, date, modify_date, p_number)
                    else:
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <a href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, id, post_file, date, modify_date,
                                           p_number)
            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template('/community/watch_doc.html', content=result, alert=alert)

    # 비 로그인 상태
    else:
        alert = """
                <script>
                    alert("로그인되지 않았습니다. 먼저 회원가입 혹은 로그인을 하세요.")
                </script>
                """
        return render_template('/sign_in.html', alert=alert)

#댓글을 작성하거나 수정(수정 내용 작성 후)했을 경우 넘어오는 경로. POST로 내용을 전달 받는다.
@app.route('/community/write_com', methods = ["POST"])
def write_com():
    if 'id' in session:
        try:
            comment_temp = request.form["comment"]

            try:
                p_number = check_p_number.return_p_number() # 클래스로 게시글 번호 가져옴.
                p_number = int(p_number)
                id_temp = session['id']
                m_number = session['number']

                sql = """
                        SELECT 1 from LIBRARY.COMMENT c
                        where c.COMMENT = '{0}' and c.MEMBER_ID = '{1}' and c.POST_NUMBER = {2}; 
                    """.format(comment_temp, id_temp, p_number)
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                i = ()
                for i in cur:
                    break
                if i == (1,):
                    result = """
                            <script>
                                alert("해당 글에 이미 같은 내용의 댓글을 달았습니다.") 
                            </script>
                            """
                    if conn:
                        conn.close()
                    return render_template('/main.html', alert=result)

                else:
                    sql = """
                            insert into LIBRARY.COMMENT (COMMENT, MEMBER_ID, DATE, MEMBER_NUMBER, POST_NUMBER) 
                            values ('{0}', '{1}', now(), {2}, {3});
                        """.format(comment_temp, id_temp, m_number, p_number)

                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()

                    # 댓글 조회 후 자동 내림차순 정렬
                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                                <div class="container">
                                                    <p>{0}</p>
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                    <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                    <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                                </div>
                                                <script>
                                                    function com_delete_check_btn_{4}(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_com?del_c_number={4}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                            """.format(comment, id, date, c_modify_date, c_number)
                    sql = """
                            SELECT p.TITLE , p.CONTENTS, p.POST_FILE, m.ID, p.DATE, p.MODIFY_DATE, p.NUMBER
                            FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER
                            where p.NUMBER ={};
                        """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, file, id, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "수정 내역 없음"

                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <br>
                                        <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?delete_com={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, id, date, modify_date, p_number)
                        else:
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <br>
                                        <a href ="{2}" download class="margin-left"><input type="button" value="첨부파일 다운로드"></a> 
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, id, date, modify_date, p_number)

            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()

            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting=comment_for_rotation_counting, content = result)

        except:
            try:
                amend_comment = request.form["amend_com"]
                amend_c_number = request.form["amend_c_number"]

                sql = """
                    SELECT c.MEMBER_ID, c.POST_NUMBER from LIBRARY.COMMENT c
                    where c.COMMENT_NUMBER = {};
                """.format(amend_c_number)

                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                data_temp = ()
                for data_temp in cur:
                    break
                amend_com_id = data_temp[0]
                amend_com_p_number = data_temp[1]
                amend_com_p_number = int(amend_com_p_number)

                sql="""
                    SELECT 1 FROM LIBRARY.COMMENT c where 
                    c.POST_NUMBER = {0}
                    and c.COMMENT ="{1}"
                    AND c.MEMBER_ID ='{2}';
                    """.format(amend_com_p_number, amend_comment, amend_com_id)

                cur = conn.cursor()
                cur.execute(sql)

                i_temp = ()
                for i_temp in cur:
                    break

                if i_temp == False:
                    result = """
                        <script>
                            alert("해당 글에 이미 같은 내용의 댓글을 작성했습니다.")
                        </script>
                        """
                    if conn:
                        conn.close

                    return render_template('/main.html', alert=result)
                else:

                    sql = """
                        UPDATE LIBRARY.COMMENT as c 
                        set c.COMMENT = '{0}', c.MODIFY_DATE =now()
                        WHERE c.COMMENT_NUMBER = {1};
                        """.format(amend_comment, amend_c_number)

                    cur=conn.cursor()
                    cur.execute(sql)
                    conn.commit()

                    sql = """
                        SELECT p.NUMBER
                        from LIBRARY.POST as p
                        where p.`NUMBER` = (SELECT c.POST_NUMBER from LIBRARY.COMMENT as c
                        where c.COMMENT_NUMBER ={});
                    """.format(amend_c_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    j = ()
                    for j in cur:
                        break
                    p_number = j[0]
                    p_number = int(p_number)

                    sql = """
                        SELECT c.COMMENT, c.MEMBER_ID, c.`DATE` , c.MODIFY_DATE, c.COMMENT_NUMBER
                        FROM LIBRARY.COMMENT as c
                        where c.POST_NUMBER = {};
                    """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    # 댓글 조회 후 자동 내림차순 정렬
                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                        <div class="container">
                                            <p>{0}</p>
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                            <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                            <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                        </div>
                                        <script>
                                            function com_delete_check_btn_{4}(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_com?del_c_number={4}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                    """.format(comment, id, date, c_modify_date, c_number)


                    sql="""
                        SELECT p.TITLE , p.CONTENTS, p.POST_FILE, m.ID, p.DATE, p.MODIFY_DATE
                        from LIBRARY.POST as p
                        left JOIN LIBRARY.`MEMBER` as m
                        on p.MEMBER_NUMBER = m.`NUMBER`
                        WHERE p.`NUMBER` = {};
                    """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, file, p_id, p_date, p_modify_date) in cur:
                        if p_modify_date == None:
                            p_modify_date = "수정 내역 없음"

                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <br>
                                        <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, p_id, p_date, p_modify_date, p_number)
                        else:
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <br>
                                        <a href ="{2}" download class="margin-left"><input type="button" value="첨부파일 다운로드"></a> 
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, p_id, p_date, p_modify_date, p_number)
            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()

            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting=comment_for_rotation_counting, content = result)

    else:
        result = ""
        result +="""
            <script>
                alert("먼저 로그인 하세요.")
            </script>
        """
        return render_template('/sign_in.html', alert = result)
# 댓글 수정 버튼 누르면 넘어 오는 라우트 함수
@app.route('/community/amend_com', methods =['GET'])
def amend_com():
    if 'id' in session:
        c_number = request.args.get('c_number')
        id = session['id']

        sql="""
            SELECT c.MEMBER_ID from LIBRARY.COMMENT as c 
            where c.COMMENT_NUMBER = '{}';
            """.format(c_number)
        conn=get_conn()
        cur=conn.cursor()
        cur.execute(sql)

        for id_test in cur:
            break
        if id_test[0] == id:

            sql= """
                SELECT COMMENT, MEMBER_ID, COMMENT_NUMBER from LIBRARY.COMMENT
                where COMMENT_NUMBER = {};
                """.format(c_number)
            conn=get_conn()
            cur=conn.cursor()
            cur.execute(sql)
            result = ""

            for (comment, c_id, c_number) in cur:
                result += """
                    <form action='/community/write_com' method="POST">
                        <p>작성자 : {1}</p><br>
                        <p>수정할 댓글 내용</p><br>
                        <textarea style="width: 100%; resize: none;" name="amend_com">{0}</textarea><br>
                        <input type="hidden" name="amend_c_number" value="{2}"><br>
                        <input type="submit" style="float:right; " value="저장" onclick=""><br>
                    </form>
                    """.format(comment, c_id, c_number)
                # amend_com.html로 넘어가서 변경 내용을 작성, 저장하면 /community/write_com로 넘어감.
            return render_template('/community/amend_com.html', content=result)

        else:

            result = """
                    <script>
                        alert("수정권한이 없습니다.") 
                    </script>
                    """
            if conn:
                conn.close()
            return render_template('/main.html', alert=result)


    else:
        alert = """
                    <script>
                        alert("로그인 후 이용하세요.")
                    </script>
                    """
        return render_template('/sign_in.html', alert=alert)

#댓글 삭제 버튼을 누르고 확인 버튼을 누르면 넘어오는 라우트 함수
@app.route('/community/delete_com', methods = ['GET'])
def delete_com():
    del_c_number = request.args.get("del_c_number")
    if 'id' in session:
        sql = """
            SELECT MEMBER_ID FROM LIBRARY.COMMENT
            where COMMENT_NUMBER ={};
            """.format(del_c_number)


        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        for data in cur:
            break
        if data[0] == session['id']:
            try:
                sql = """
                    DELETE FROM LIBRARY.COMMENT
                    where COMMENT_NUMBER ={0};
                    """.format(del_c_number)
                cur=conn.cursor()

                cur.execute(sql)
                conn.commit()
            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()

            return render_template('/main.html')

        #로그인한 사용자가 다른 회원의 댓글을 삭제하려는 경우
        else:
            alert = """
                        <script>
                            alert("삭제 권한이 없습니다.")
                        </script>
                    """
            return render_template('/main.html', alert=alert)

    else:
        alert = """
                <script>
                    alert("로그인되지 않았습니다. 먼저 회원가입 혹은 로그인을 하세요.")
                </script>
            """
        return render_template('/sign_in.html', alert=alert)

@app.route('/community/check_login')
def check_login():
    if 'id' in session: # session에 id 값이 있다면(로그인이 돼 있다면)
        author = session['id']
        return render_template("/community/write_doc.html", author = author)
    else:
        alert = """
            <script>
                alert("글을 작성하려면 회원가입 혹은 로그인을 하세요.")
            </script>
            """
        return render_template('/sign_in.html', alert = alert )

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


class remeber_p_number():

    def __init__(self):
        self.post_number_cl = ''

    def insert_p_number(self,number):
        self.post_number_cl = number

    def return_p_number(self):
        return self.post_number_cl


if __name__ == "__main__":
    check_p_number = remeber_p_number()
    app.secret_key = 'app secret key'
    app.run(host='0.0.0.0')







