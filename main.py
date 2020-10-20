import mariadb
import sys, datetime

from flask import Flask, render_template, request

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
    return render_template("/main.html")

@app.route('/sign_in')
def sign_in():
    return render_template("/sign_in.html")

@app.route('/sign_in', methods=['POST'])
def check_id():
    insert_id = request.form['id']
    insert_pw = request.form['pw']
    result =""

    sql = "SELECT ID, PW FROM MEMBER WHERE ID = '{}'".format(insert_id)
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        for (ID, PW) in cur:
            result = "{0},{1}".format(ID,PW)

            if ID == insert_id :
                if PW == insert_pw :
                    print("로그인이 되었습니다")
                else: print("비밀번호가 일치하지 않습니다")
            else: print("아이디가 일치하지 않습니다")

    except mariadb.Error as e:
        print("ERR: {}".format(e))
        sys.exit(1)
    except TypeError as e:
        result = ""
    if conn:
        conn.close()

    print(result)

    return render_template('/main.html')

@app.route('/sign_up')
def sign_up():
    return render_template("/sign_up.html")

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

@app.route('/member_info')
def member_info():
    r_num = "1"
    sql = "SELECT NUMBER, ID, PW, PHONE, EMAIL, GENDER, NAME, BIRTHDAY FROM MEMBER WHERE NUMBER = {}".format(r_num)
    result = ""

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

    except mariadb.Error:
        result = "사용자 없음."    
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/member_info.html", content=result)

@app.route('/member_info', methods=['POST'])
def member_info_modify():
    id = request.form["id"]
    pw = request.form["pw"]
    name = request.form["name"]
    gender = request.form["gender"]
    birth= request.form["birthday"]
    phone = request.form["phone"]
    email = request.form["email"]
    sql = "UPDATE MEMBER SET pw='{0}',name='{1}',gender='{2}',birthday='{3}',phone='{4}',email='{5}' WHERE id='{6}'".format(pw, name, gender, birth, phone, email, id)

    try:
        conn = get_conn()
        cur = conn.cursor()
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

    return render_template("/master/community.html", content = result, content1 = for_rotation_counting)

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

