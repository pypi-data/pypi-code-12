import sys
import sqlite3
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic
import re
import xlwt

form_class = uic.loadUiType("..\\main_window.ui")[0]


class MyWindow(QMainWindow, form_class):

    selected_file_name =''
    selected_saved_file_name=''

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    @pyqtSlot()
    def on_button1(self):
        name = QFileDialog.getOpenFileName(self, '스크립트수행화일열기',filter='*.txt')
        if name == '' :
            return

        file = open(name,'r')

        self.selected_file_name = str(name)

        with file:
            text = file.read()
            self.textEdit.setText(text)

    @pyqtSlot()
    def on_button2(self):
        name = QFileDialog.getSaveFileName(self, 'Save File',filter='*.xls')
        if name == '':
            return

        file = open(name,'w')
        self.selected_saved_file_name = str(name)
        #text = self.textEdit.toPlainText()
        #file.write(text)
        file.close()
        self.export_excel()

    def export_excel(self):
        conn = sqlite3.connect('insider.db')
        query = conn.cursor()

        workbook = xlwt.Workbook(encoding='utf-8')
        workbook.default_style.font.height = 20*11

        worksheet = workbook.add_sheet(u'취약점점검-윈도우즈')



        wisi =''

        fin = open(self.selected_file_name,'rt')

        for line in fin:
           wisi  += line
        fin.close()

        p = re.compile('[W'+'\w\d\|[-]+\d+'+']'+'\s\w*')
        result = p.findall(wisi)

        start_time_re = re.compile('Start Time  ####################################  '+'\n\d{4}[-]\d{2}[-]\d{2}',re.DOTALL)
        host_name_re = re.compile('Host Name.*')
        ipv4_address_re = re.compile('IPv4 Address.*')
        os_version_re = re.compile('OS Name.*')

        start_time_ma = re.findall(start_time_re,wisi)
        host_name_ma = re.search(host_name_re,wisi)
        ipv4_address_ma = re.findall(ipv4_address_re,wisi)
        os_version_ma = re.search(os_version_re,wisi)


        host_name_ma_result =host_name_ma.group()
        os_version_ma_result = os_version_ma.group()

        seperator = ':'

        str_start_time_ma = str(start_time_ma)
        start_time_c = str_start_time_ma[-12:]
        strart_time_c1 = start_time_c[0:10]

        idx_2 = host_name_ma_result.index(seperator)
        host_name_c = host_name_ma_result[idx_2+1 :]

        joined = seperator.join(ipv4_address_ma)
        idx_3 = joined.index(seperator)
        ipv4_address_c = joined[idx_3+1 :]

        idx_4 = os_version_ma_result.index(seperator)
        os_version_c = os_version_ma_result[idx_4+1 :]
        os_version__c_strip = os_version_c.strip()

        query.execute("DELETE FROM insider WHERE start_time =? AND host_name =?",(strart_time_c1,host_name_c))
        query.execute("CREATE TABLE IF NOT EXISTS insider_exe (start_time REAL,host_name REAL,selected_file_name REAL,"
                      "selected_saved_file_name REAL)")
        query.execute("DELETE FROM insider_exe WHERE start_time = ? AND host_name = ? ",(strart_time_c1,host_name_c))

        query.execute("INSERT INTO insider_exe (start_time,host_name,selected_file_name,selected_saved_file_name)"
                              "VALUES (?, ?, ?, ?)",
                              (strart_time_c1,host_name_c,self.selected_file_name,self.selected_saved_file_name))
        conn.commit()

        i=0
        for j in range(0,len(result)):

            m = result[j]

            if m[-3:]=='END':
                n= result[j+1]
                yn_good_c =n[-2:]
                if yn_good_c == "양호":
                    yn_good_cc ="양호"
                    style = xlwt.easyxf('font: bold 1,color black')
                elif yn_good_c == "취약":
                    yn_good_cc ="취약"
                    style = xlwt.easyxf('font: bold 1, color red')
                elif yn_good_c == "수동":
                    yn_good_cc ="수동"
                    style = xlwt.easyxf('font: bold 1,color black')
                else:
                    yn_good_cc = "진행중"
                    style = xlwt.easyxf('font: bold 1,color black')

                check_ma='CHECKED'
                master_index_c = m[1:-5]

                if master_index_c == 'W-1' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'Administrator 계정 이름 바꾸기'
                    test_time = '단기'

                elif master_index_c == 'W-2' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'Guest 계정 상태'
                    test_time = '단기'

                elif master_index_c == 'W-3' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = '불필요한 계정 제거'
                    test_time = '단기'

                elif master_index_c == 'W-4' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = '계정 잠금 임계값 설정'
                    test_time = '단기'

                elif master_index_c == 'W-5' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = '해독 가능한 암호화를 사용하여 암호 저장'
                    test_time = '단기'

                elif master_index_c == 'W-6' :
                    test_type_c = '계정관리'
                    test_grade_c = '상'
                    test_type_desc_c = '관리자 그룹에 최소한의 계정 포함'
                    test_time = '단기'

                elif master_index_c == 'W-7' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'Everyone 사용 권한으 익명 사용자에게 적용'
                    test_time = '단기'

                elif master_index_c == 'W-8' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '계정 잠금 기간 설정'
                    test_time = '단기'

                elif master_index_c == 'W-9' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '패스워드 복잡성 설정'
                    test_time = '장기'

                elif master_index_c == 'W-10' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '패스워드 최소 암호 길이'
                    test_time = '단기'

                elif master_index_c == 'W-11' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '패스워드 최대 사용 기간'
                    test_time = '단기'

                elif master_index_c == 'W-12' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '패스워드 최소 사용 기간'
                    test_time = '단기'

                elif master_index_c == 'W-13' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '마지막 사용자 이름 표시 안함'
                    test_time = '단기'

                elif master_index_c == 'W-14' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '로컬 로그온 허용'
                    test_time = '단기'

                elif master_index_c == 'W-15' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '익명 SID/이름 변환 허용'
                    test_time = '단기'

                elif master_index_c == 'W-16' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '최근 암호 기억'
                    test_time = '중기'

                elif master_index_c == 'W-17' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '콘솔 로그온 시 로클 계정에서 빈 암호 사용 제한'
                    test_time = '단기'

                elif master_index_c == 'W-18' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '원격 터미널 접속 가능한 사용자 그룹 제한'
                    test_time = '단기'

                elif master_index_c == 'W-19' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '공유 권한 및 사용자 그룹 설정'
                    test_time = '단기'

                elif master_index_c == 'W-20' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '하드디스크 기본 공유 제거'
                    test_time = '단기'

                elif master_index_c == 'W-21' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '불필요한 서비스 제거'
                    test_time = '단기'

                elif master_index_c == 'W-22' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 서비스 구동 점검'
                    test_time = '단기'

                elif master_index_c == 'W-23' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 디렉터리 리스팅 제거'
                    test_time = '단기'

                elif master_index_c == 'W-24' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS CGI 실행 제한'
                    test_time = '단기'

                elif master_index_c == 'W-25' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 상위 디렉터리 접근 금지'
                    test_time = '단기'

                elif master_index_c == 'W-26' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 불필요한 파일 제거'
                    test_time = '단기'

                elif master_index_c == 'W-27' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 웹 프로세스 권한 제한'
                    test_time = '단기'

                elif master_index_c == 'W-28' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 링크 사용금지'
                    test_time = '단기'

                elif master_index_c == 'W-29' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 파일 업로드 및 다운로드 제한'
                    test_time = '단기'

                elif master_index_c == 'W-30' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS DB 연결 취약점 점검'
                    test_time = '단기'

                elif master_index_c == 'W-31' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 가상 디렉터리 삭제'
                    test_time = '단기'

                elif master_index_c == 'W-32' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 데이터 파일 ACL 적용'
                    test_time = '단기'

                elif master_index_c == 'W-33' :
                    test_type_c = '파일 및 디렉리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 미사용 스크립트 매핑 제거'
                    test_time = '단기'

                elif master_index_c == 'W-34' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS Exec 명령어 쉘 호출 진단'
                    test_time = '중기'

                elif master_index_c == 'W-35' :
                    test_type_c = '파일 및 디렉터리 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS WebDAV 비활성화'
                    test_time = '중기'

                elif master_index_c == 'W-36' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'NetBIOS 바인딩 서비스 구동 점검'
                    test_time = '중기'

                elif master_index_c == 'W-37' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'FTP 서비스 구동 점검'
                    test_time = '단기'

                elif master_index_c == 'W-38' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'FTP 디렉터리 접근권한 설정'
                    test_time = '중기'

                elif master_index_c == 'W-39' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'Anonymous FTP 금지'
                    test_time = '단기'

                elif master_index_c == 'W-40' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'FTP 접근 제어 설정'
                    test_time = '중기'

                elif master_index_c == 'W-41' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'DNS Zone Transfer 설정'
                    test_time = '단기'

                elif master_index_c == 'W-42' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'RDS(RemoteDataServices)제거'
                    test_time = '중기'

                elif master_index_c == 'W-43' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '최신 서비스팩 적용'
                    test_time = '중기'

                elif master_index_c == 'W-44' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '터미널 서비스 암호화 수준 설정'
                    test_time = '단기'

                elif master_index_c == 'W-45' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'IIS 웹서비스 정보 숨김'
                    test_time = '단기'

                elif master_index_c == 'W-46' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'SNMP 서비스 구동 점검'
                    test_time = '단기'

                elif master_index_c == 'W-47' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'SNMP 서비스 커뮤니티스트링의 복잡성 설정'
                    test_time = '단기'

                elif master_index_c == 'W-48' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'SNMP Access control 설정'
                    test_time = '단기'

                elif master_index_c == 'W-49' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'DNS 서비스 구동 점검'
                    test_time = '단기'

                elif master_index_c == 'W-50' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '하'
                    test_type_desc_c = 'HTTP/FTP/SMTP 배너 차단'
                    test_time = '중기'

                elif master_index_c == 'W-51' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'Telnet 보안 설정'
                    test_time = '중기'

                elif master_index_c == 'W-52' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '불필요한 ODBC/OLE-DB 데이터 소스와 드라이브 제거'
                    test_time = '중기'

                elif master_index_c == 'W-53' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '원격터미널 접속 타임아웃 설정'
                    test_time = '단기'

                elif master_index_c == 'W-54' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '예약된 작업에 의심스러운 명령이 등록되어 있는지 점검'
                    test_time = '중기'

                elif master_index_c == 'W-55' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '최신 HOT FIX 적용'
                    test_time = '중기'

                elif master_index_c == 'W-56' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '백신 프로그램 업데이트'
                    test_time = '단기'

                elif master_index_c == 'W-57' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '정책에 따른 시스템 로깅 설정'
                    test_time = '단기'

                elif master_index_c == 'W-58' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '로그의 정기적 검토 및 보고'
                    test_time = '중기'

                elif master_index_c == 'W-59' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '원격으로 액세스할 수 있는 레지스트리 경로'
                    test_time = '단기'

                elif master_index_c == 'W-60' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '하'
                    test_type_desc_c = '이벤트 로그 관리 설정'
                    test_time = '중기'

                elif master_index_c == 'W-61' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '원격에서 이벤트 로그 파일 접근 차단'
                    test_time = '중기'

                elif master_index_c == 'W-62' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '백신 프로그램 설치'
                    test_time = '단기'

                elif master_index_c == 'W-63' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'SAM 파일 접근 통제 설정'
                    test_time = '중기'

                elif master_index_c == 'W-64' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '화면보호기 설정'
                    test_time = '단기'

                elif master_index_c == 'W-65' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '로그온하지 않고 시스템 종료 허용'
                    test_time = '중기'

                elif master_index_c == 'W-66' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '원격 시스템에서 강제로 시스템 종료'
                    test_time = '단기'

                elif master_index_c == 'W-67' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '보안 감사를 로그할 수 없는 경우 즉시 시스템 종료'
                    test_time = '단기'

                elif master_index_c == 'W-68' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'SAM 계정과 공유의 익명 열거 허용 안함'
                    test_time = '단기'

                elif master_index_c == 'W-69' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = 'Autologon 기능 제어'
                    test_time = '단기'

                elif master_index_c == 'W-70' :
                    test_type_c = '서비스 관리'
                    test_grade_c = '상'
                    test_type_desc_c = '이동식 미디어 포맷 및 꺼내기 허용'
                    test_time = '단기'

                elif master_index_c == 'W-71' :
                    test_type_c = '패치관리'
                    test_grade_c = '상'
                    test_type_desc_c = '디스크 볼륨 암호화 설정'
                    test_time = '단기'

                elif master_index_c == 'W-72' :
                    test_type_c = '로그관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'DoS 공격 방어 레지스트리 설정'
                    test_time = '중기'

                elif master_index_c == 'W-73' :
                    test_type_c = '로그관리'
                    test_grade_c = '중'
                    test_type_desc_c = '사용자가 프린터 드라이버를 설치할 수 없게 함'
                    test_time = '중기'

                elif master_index_c == 'W-74' :
                    test_type_c = 'DB 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '세션 연결을 중단하기 전에 필요한 유휴시간'
                    test_time = '단기'

                elif master_index_c == 'W-75' :
                    test_type_c = 'DB 관리'
                    test_grade_c = '하'
                    test_type_desc_c = '경고 메시지 설정'
                    test_time = '단기'

                elif master_index_c == 'W-76' :
                    test_type_c = 'DB 관리'
                    test_grade_c = '중'
                    test_type_desc_c = '사용자별 홈 디렉터리 권한 설정'
                    test_time = '단기'

                elif master_index_c == 'W-77' :
                    test_type_c = 'DB 관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'LAN Manager 인증 수준'
                    test_time = '중기'

                elif master_index_c == 'W-78' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '보안 채널 데이터 디지털 암호화 또는 서명'
                    test_time = '단기'

                elif master_index_c == 'W-79' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '파일 및 디렉터리 보호'
                    test_time = '단기'

                elif master_index_c == 'W-80' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '컴퓨터 계정 암호 최대 사용 기간'
                    test_time = '단기'

                elif master_index_c == 'W-81' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = '시작프로그램 목록 분석'
                    test_time = '단기'

                elif master_index_c == 'W-82' :
                    test_type_c = '계정관리'
                    test_grade_c = '중'
                    test_type_desc_c = 'Windows 인증 모드 사용'
                    test_time = '단기'


                worksheet.write(i, 0, host_name_c,style)
                worksheet.write(i, 1, ipv4_address_c,style)
                worksheet.write(i, 2, os_version__c_strip,style)
                worksheet.write(i, 3, test_type_c,style)
                worksheet.write(i, 4, master_index_c,style)
                worksheet.write(i, 5, test_type_desc_c,style)
                worksheet.write(i, 6, test_grade_c,style)
                worksheet.write(i, 7, test_time,style)
                worksheet.write(i, 8, yn_good_cc,style)

                workbook.save(self.selected_saved_file_name)

                query.execute("CREATE TABLE IF NOT EXISTS insider"+
                              "(start_time REAL,"+
                              "host_name REAL,"+
                              "ipv4_address REAL,"+
                              "os_version REAL,"+
                              "test_type REAL,"+
                              "master_index REAL,"+
                              "text_type_desc REAL,"+
                              "test_grade REAL,"+
                              "test_time REAL,"+
                              "yn_good REAL)")

                query.execute("INSERT INTO insider (start_time,host_name, ipv4_address, os_version, test_type,master_index,"+
                              "text_type_desc,test_grade,test_time,yn_good) "
                              "VALUES (?,?, ?, ?, ?,?,?,?,?,?)",
                              (strart_time_c1,host_name_c, ipv4_address_c, os_version__c_strip, test_type_c,master_index_c,test_type_desc_c,test_grade_c,test_time,yn_good_cc))
                i=i+1

            conn.commit()
        conn.close()
    @pyqtSlot()
    def on_button3(self):
        conn = sqlite3.connect('insider.db')
        query1 = conn.cursor()
        self.tableWidget_2.setRowCount(20)
        self.tableWidget_2.setColumnCount(4)
        column_headers1 = ['스크립트날짜', 'Host명', '스크립트실행화일','스크립트엑셀저장화일']
        self.tableWidget_2.setHorizontalHeaderLabels(column_headers1)
        data1 = query1.execute('SELECT start_time,host_name, selected_file_name, selected_saved_file_name FROM insider_exe')

        index=0
        for row in data1:
            self.tableWidget_2.setItem(index,0,QTableWidgetItem(str(row[0])))
            self.tableWidget_2.setItem(index,1,QTableWidgetItem(str(row[1])))
            self.tableWidget_2.setItem(index,2,QTableWidgetItem(str(row[2])))
            self.tableWidget_2.setItem(index,3,QTableWidgetItem(str(row[3])))

            index = index+1
        self.tableWidget_2.resizeColumnsToContents()
        self.tableWidget_2.resizeRowsToContents()
        conn.close()
    @pyqtSlot()
    def on_button4(self):
        self.tableWidget.setRowCount(82)
        self.tableWidget.setColumnCount(9)
        column_headers = ['호스트명', 'IP Address', 'OS Version','점검분류','항목번호','취약점점검항목','등급',
                          '조치시기','점검결과']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        try :
                conn = sqlite3.connect('insider.db')
                query = conn.cursor()
                data = query.execute('SELECT host_name, ipv4_address, os_version, test_type,master_index,text_type_desc,'
                              'test_grade,test_time,yn_good FROM insider')

                index=0
                for row in data:
                    self.tableWidget.setItem(index,0,QTableWidgetItem(str(row[0])))
                    self.tableWidget.setItem(index,1,QTableWidgetItem(str(row[1])))
                    self.tableWidget.setItem(index,2,QTableWidgetItem(str(row[2])))
                    self.tableWidget.setItem(index,3,QTableWidgetItem(str(row[3])))
                    self.tableWidget.setItem(index,4,QTableWidgetItem(str(row[4])))
                    self.tableWidget.setItem(index,5,QTableWidgetItem(str(row[5])))
                    self.tableWidget.setItem(index,6,QTableWidgetItem(str(row[6])))
                    self.tableWidget.setItem(index,7,QTableWidgetItem(str(row[7])))
                    self.tableWidget.setItem(index,8,QTableWidgetItem(str(row[8])))

                    index = index+1
                self.tableWidget.resizeColumnsToContents()
                self.tableWidget.resizeRowsToContents()
        except sqlite3.Error as e :
                print ('Error %s :' % e.args[0])
                sys.exit(1)
        finally:
                if conn:
                    conn.close()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()