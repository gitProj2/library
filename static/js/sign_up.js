// 파라미터 obj 객체 삭제 
function check_btn(obj) {
    obj.parentNode.removeChild(obj);
}

// 아이디 중복체크
function id_double_check(id, obj) {
    var httpRequest = new XMLHttpRequest();

    httpRequest.onreadystatechange = check_id;
    httpRequest.open('POST', '/check_id?id='+ new_id);
    httpRequest.send();

    function check_id() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                var ck_id = document.getElementById('id');
                var button = document.getElementById('id')
                button.getAttribute("ID 중복확인")
                    if ck_id == id  {
                        alert("사용 불가능한 ID 입니다.")
                    
                    } else {
                        alert("사용가능한 ID 입니다.");
                    }
                    alert(httpRequest.responseText);
            } else {
                alert('통신에 이상이 발생했습니다.');
                }
            }
        }
      
    }


