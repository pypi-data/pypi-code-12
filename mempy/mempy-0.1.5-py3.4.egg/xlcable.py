# *-* coding: UTF-8 -*-
#==============================================================================
"""
[xlcable.py] - Mempire Excel-Python Link module

이 모듈은 Microsoft Excel과 Python 연결 기능을 구현한 모듈입니다.

"""
__author__ = 'Herokims'
__verion__ = '0.1.4'
__since__ = '2015-05-11'
__update__ = '2016-06-09'
__copyright__ = 'Copyright (c) TreeInsight.org'
__engine__ = 'Python 3.4.1'
#==============================================================================


import numpy as np
import pandas as pd
from win32com import client

try:
    from .lib import easygui as i
except:
    from lib import easygui as i 


def xl2py(workbookname, sheetname, source=None, blocksize=30000, gui=False):
#작성일시 : 2015. 5. 11. (최종수정 : 2015. 5. 22.)
#입력설명 : workbookname은 열려있는 워크북이름(또는 워크북파일 경로)
#          sheetname은 워크시트이름
#          source는 데이터를 가져올 Range의 주소튜플
#          blocksize는 데이터블록으로 분할전송시 블록의 크기
#          gui는 진행메시지를 GUI(MsgBox형태)로 보여줄 것인지 여부
#출력설명 : 성공하면 pandas DataFrame객체, 실패하면 None객체를 반환한다.
#주의사항 : 1. source는 튜플타입 
#             (좌측상단셀 행번호,좌측상단셀 열번호,우측하단셀 행번호,우측하단셀 열번호)
#          2. source를 지정하지 않으면 A1셀부터 UsedRange까지를 반환한다.
#기능설명 : 
    '''
    ===================================================================================
    xl2py(workbookname, sheetname, source=None, blocksize=30000, gui=False): 
    -----------------------------------------------------------------------------------    
    지정하는 Excel 워크북의 지정하는 워크시트에서 data를 가져와 pandas DataFrame객체로 반환한다.
    -----------------------------------------------------------------------------------
    ex. 
        df = xl2py("통합 문서20", "Sheet1")
        df = xl2py("통합 문서20", "Sheet1", gui=True)
        df = xl2py("통합 문서3", "Sheet1", (1,1,17,18))
        df = xl2py("test.xlsm","Sheet3")    
        df = xl2py("Book1.xlsm","Sheet3",(2,1,3,3)) 
        df = xl2py("c:\\\\test.xlsm","Sheet3",(2,1,10,18)) 
        df = xl2py("통합 문서19","Sheet1",blocksize=500)
    ===================================================================================
    '''  
    
    
    #메모리에 존재하는 Excel을 찾고, 없으면 새로 로딩
    try:
        xl = client.GetObject(Class="Excel.Application")
    except:
        msg = "\nMicrosoft Excel이 설치되어 있지 않습니다!" 
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg) 
            
        return None
    
    if float(xl.Version) < 12:
        msg = "\nExcel 2007 이상 버전이 필요합니다!"  
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg) 
            
        return None
    
    try:
        ws = xl.Workbooks(workbookname).Worksheets(sheetname)
    except:
        try:
            ws = xl.Workbooks.Open(workbookname).Worksheets(sheetname)
        except: 
            msg = "\n지정하는 워크북 또는 워크시트를 찾을 수 없습니다!" 
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg) 
                
            return None
    
    #source가 지정되지 않은 경우는 대상 시트의 UsedRange 사용
    #(아무런 내용이 없는 경우에도 range_rowend와 range_colend는 각각 1로 반환)
    if source is None:
        try:
            range_rowstart = 1
            range_rowend = ws.UsedRange.Row + ws.UsedRange.Rows.Count - 1
            range_colstart = 1            
            range_colend = ws.UsedRange.Column + ws.UsedRange.Columns.Count - 1
        except:
            msg = "\n지정하는 워크시트의 UsedRange를 찾을 수 없습니다!" 
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg)  
                
            return None 
    else:
        try:
            range_rowstart = int(source[0])
            range_colstart = int(source[1])
            range_rowend = int(source[2])
            range_colend = int(source[3])   
        except:
            msg = "\nsource가 올바른 형식이 아닙니다!" 
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg) 
                
            return None
    
    if range_rowstart < 1 or range_colstart < 1 or \
       range_rowend < 1 or range_colend < 1 or \
       range_rowend < range_rowstart or range_colend < range_colstart or \
       range_rowend > 1048576 or range_colend > 16384:
           
        msg = "\nsource가 올바른 형식이 아니거나, Excel의 범위를 벗어났습니다!" 
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg) 
            
        return None        
           
    try:
        xldata_raw = ws.Range(ws.Cells(range_rowstart,range_colstart),\
                              ws.Cells(range_rowend,range_colend)).Value
        xldata = np.array(xldata_raw)

        #데이터에 따라, index과 label을 따로 가지고 있지 않을 수도 있으므로 디폴트 변환한다.
        df = pd.DataFrame(xldata)
        
        return df
    
    #이 부분에서는 Memory용량 때문에 오류났을 가능성이 높음
    except:
     
        if ws is None:
            ws = xl.Workbooks(workbookname).Worksheets(sheetname)
        
        #대상 시트의 A1셀에만 데이터가 있는 경우에는 데이터를 List로 만들어 입력해야만
        #DataFrame을 만들 수 있음('ValueError(Must pass 2-d input)'에러 발생)         
        if range_rowstart == range_rowend == \
           range_colstart == range_colend == 1:
               
            df = pd.DataFrame(np.array([ws.Range("A1").Value,]))  
              
            return df
            
        try:
            msg = "\n데이터블록으로 나누어 받습니다..\n" 
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg) 
            
            pagenum,tmp  = divmod(range_rowend,blocksize)                
            pagenum += 1    #최종 pagenum은 남은 부분을 담을 페이지까지 포함해서 결정
            
            #blocksize만큼 page로 나누어 로딩하고(1번째 ~ pagenum-1번째),        
            for p_index in range(pagenum-2):
    
                xldata_raw = None
                xldata_raw = ws.Range(ws.Cells(p_index * blocksize+1,1),\
                                  ws.Cells((p_index+1)*blocksize,range_colend)).Value
                
                xldata = np.array(xldata_raw)
                
                df_part = None
                df_part = pd.DataFrame(xldata)    
                
                if p_index == 0:
                    df = df_part
                else:
                    df = df.append(df_part,ignore_index=True)  
                    
                if gui:
                    pass
                else:
                    print("%2d/%d 데이터블록 받음" % (p_index+1,pagenum)) 
                
    
            #남은 부분을 로딩한다(pagenum번째).
            xldata_raw = None
            xldata_raw = ws.Range(ws.Cells((pagenum-1)*blocksize + 1,1),\
                                  ws.Cells(range_rowend,range_colend)).Value
            
            xldata = np.array(xldata_raw)
            
            df_part = None
            df_part = pd.DataFrame(xldata)
            
            df = df.append(df_part,ignore_index=True)
            
            if gui:
                pass
            else:
                print("%2d/%d 데이터블록 받음" % (pagenum,pagenum)) 
            
            #성공 메시지는 분할송수신의 경우에만 한정
            msg = "\n데이터블록 수신이 성공했습니다.\n" 
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg) 
                
            return df
            
        except Exception as e:
            msg = "\n알 수 없는 에러가 발생하여 df를 만들지 못했습니다!\n" + \
                  "(너무 큰 blocksize가 원인일 수 있습니다)" 
            
            if gui:
                i.msgbox(e.args)
                i.msgbox(msg)
            else:
                print(e.args)
                print(msg) 
                
            return None
    

def py2xl(data, workbookname=None, sheetname=None, target=None, blocksize=30000, gui=False):
#작성일시 : 2015. 5. 11. (최종수정 : 2015. 5. 22.)
#입력사항 : data는 pandas DataFrame객체, 
#          workbookname은 데이터를 전송하고자 하는 워크북(미입력시 새 워크북),
#          sheetname은 데이터를 전송하고자 하는 워크시트(미입력시 새 시트),
#          target은 데이터를 입력할 위치의 좌측상단셀의 (행번호,열번호) 튜플(미입력시 (1,1))
#          blocksize는 데이터블록전송시 블록크기(미입력시 30000)
#          gui는 진행메시지를 GUI(MsgBox형태)로 보여줄 것인지 여부
#출력사항 : 성공하면 1, 실패하면 0
#주의사항 : 없음
#기능설명 : 
    '''
    ===================================================================================
    py2xl(data, workbookname=None, sheetname=None, target=None, blocksize=30000, gui=False): 
    -----------------------------------------------------------------------------------
    data(pandas DataFrame객체)를 지정하는 Excel 워크북(미입력시 새 워크북)으로 전송한다.
    -----------------------------------------------------------------------------------    
    ex. 
        py2xl(df)
        py2xl(df, target=(2,2))
        py2xl(df, target=(2,2), gui=True)
        py2xl(df, None, None, (2,2))
        py2xl(df, blocksize=10000)
        py2xl(df, "writedoc")
        py2xl(df, "doc1.xlsx")
        py2xl(df, "통합 문서10.xlsx", "Sheet1", (3,3))
        py2xl(df, "통합 문서9.xlsx", None, (3,3))
        py2xl(df, "통합 문서9.xlsx", target=(3,3))
        py2xl(df, "d:\\\\doc4.xlsx", "Sheet2", (1,3))
        py2xl(df, "d:\\\\통합 문서10.xlsx", target=(3,3))
    ===================================================================================
    '''  
   
    
    if data is None:
        msg = "data변수가 비어있습니다!" 
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg) 

        return 0
    
    if target is None:
        target = (1,1) #디폴트값은 A1셀

    if target[0] > 1048576 or target[0] < 1 or \
       target[1] > 16384 or target[1] < 1:
        msg = "data를 붙여넣을 위치가 Excel 시트의 범위를 넘습니다!" 
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg)   
            
        return 0

    if target[0] + data.values.shape[0] > 1048576 or \
       target[1] + data.values.shape[1] > 16384:
        msg = "붙여넣을 위치와 data 크기의 합이 Excel 시트의 범위를 넘습니다!"
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg)   

        return 0
    
    #메모리에 존재하는 Excel을 찾고, 없으면 새로 로딩
    try:
        xl = client.GetObject(Class="Excel.Application")
    except:
        msg = "\nMicrosoft Excel이 설치되어 있지 않습니다!"
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg)  

        return 0
        
    if float(xl.Version) < 12:
        msg = "\nExcel 2007 이상 버전이 필요합니다!"
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg)  

        return None
    
    #wb_new(Workbook)를 구한다.
    if workbookname is None:
        wb_new = xl.Workbooks.Add()
        sheetname = "Sheet1"
    else:
        #workbookname이 경로명을 포함한 경우
        #(아직 열리지 않은 엑셀파일을 열고자 하는 경우)
        if "\\" in workbookname:
            try:
                wb_new = xl.Workbooks.Open(workbookname)
            except:
                wb_new = xl.Workbooks.Add()
                sheetname = "Sheet1"
        
        #파일명인 경우
        else:
            #로딩되어 있을 수 있으므로, 일단 열어보고,
            try:
                wb_new = xl.Workbooks(workbookname)
          
            #안되면, 경로를 붙여서 파일을 열어보고
            except:
                try:
                    wbpath = str(xl.Workbooks(workbookname).Path)
                    wbpath = wbpath + "\\" + workbookname                          
                    wb_new = xl.Workbooks.Open(wbpath)
                
                #그래도 안되면 새로 생성한다.
                except:
                    wb_new = xl.Workbooks.Add()
                    sheetname = "Sheet1"
       
       
    #ws(Worksheet)를 구한다.
    if sheetname is None:
        ws = wb_new.Worksheets.Add()
    else:
        try:
            ws = wb_new.Worksheets(sheetname)
        except:
            ws = wb_new.Worksheets.Add()


    xl.Visible = True     
    
    try:
        #효율적인 전송을 위해 데이터블록 전송방식으로 바로 넘어감
        raise Exception
        
        #--------------------------------------------------------------------------------
        #이 부분은 데이터를 통째로 전송하기 위한 부분으로 사실상 사용하지 않음
        ws.Range(ws.Cells(1,1),ws.Cells(len(data.index)-1,len(data.columns)-1)).Value = \
                                            data.values.tolist()
        #--------------------------------------------------------------------------------
        
        msg = "\n데이터 전송이 성공했습니다.\n"
        
        if gui:
            i.msgbox(msg)
        else:
            print(msg)  

        return 1
        
    except:
        
        try:
            range_rowend = data.values.shape[0]
            range_colend = data.values.shape[1]
            
            msg = "\n'" + wb_new.name + "'에 데이터블록으로 나누어 보냅니다..\n"
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg)  

            pagenum,tmp  = divmod(range_rowend,blocksize)                
            pagenum += 1    #최종 pagenum은 남은 부분을 담을 페이지까지 포함해서 결정
            
            #blocksize만큼 page로 나누어 로딩하고(1번째 ~ pagenum-1번째),        
            for p_index in range(pagenum-1):
    
                data_part = None
                data_part = data[p_index*blocksize:(p_index+1)*blocksize]
                ws.Range(ws.Cells(p_index*blocksize+target[0],target[1]),\
                         ws.Cells(p_index*blocksize+target[0]+len(data_part.index)-1,target[1]+len(data_part.columns)-1)).Value = \
                             data_part.values.tolist()
                    
                if gui:
                    pass
                else:
                    print("%2d/%d 데이터블록 보냄" % (p_index+1,pagenum))
                    
            #남은 부분을 로딩한다(pagenum번째).
            data_part = None
            data_part = data[(pagenum-1)*blocksize:]
            
            ws.Range(ws.Cells((pagenum-1)*blocksize+target[0],target[1]),\
                     ws.Cells((pagenum-1)*blocksize+target[0]+len(data_part.index)-1,target[1]+len(data_part.columns)-1)).value = \
                            data_part.values.tolist()
            
            if gui:
                pass
            else:
                print("%2d/%d 데이터블록 보냄" % (pagenum,pagenum))  

            #성공 메시지는 분할송수신의 경우에만 한정
            msg = "\n데이터블록 전송이 성공했습니다.\n"
            
            if gui:
                i.msgbox(msg)
            else:
                print(msg) 
                
            return 1                
            
        except Exception as e:
            msg = "Excel 데이터블록 전송과정에서 에러가 발생했습니다!\n" + \
                  "(너무 큰 blocksize가 원인일 수 있습니다)" 
            
            if gui:
                i.msgbox(e.args)
                i.msgbox(msg)
            else:
                print(e.args)
                print(msg) 
                
            return 0 
        

if __name__ == "__main__":
    pass
