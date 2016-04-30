import sys
import datetime
out=''
def run(md, title):
    global out
    out=''
    bold=0
    escapeMd=''
    imageUrl=''
    imageAlt=''
    isStyle=False
    isHeading=False
    footerContent=''
    style=False
    styleContent=''
    cssCodeClass=''
    cssSupClass=''
    beforeSize=''
    color="black"
    lineSize=0
    lineLength=0
    linkText=''
    link=''
    fixBr=''
    if title==0:
        title=(str(datetime.datetime.now())[:-7])
    line=0
    isCode=False
    isSup=False
    isHtml=False
    size="medium"
    align='left'
    def createspan():
        global out
        out=out+'</span><span '+cssCodeClass+cssSupClass+'style="font-weight: '+('normal','bold')[bold]+'; text-decoration: '+('none','underline','line-through','overline')[line]+'; font-style: '+('normal','oblique','italic')[style]+'; font-size: '+size+'; text-align: '+align+'; '+styleContent+'" >'
    out=out+"""<!DOCTYPE html>
    <html>
    <head>
        <style>.code {background-color:#EEEEEE;font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New;} .sup { vertical-align: super; }</style>
        <title>"""+title+"""</title>
    </head>
    <body>\n"""
    out=out+('<span>')
    createspan()
    while len(md) > 0:
        if md[0]=='\\':
            md=md[1:]
            out=out+(md[0])
            md=md[1:]
            continue
        if md[0]=='@':
            ucode=''
            while True:
                md=md[1:]
                if md[0] not in '0123456789':
                    break
                ucode+=md[0]
            if len(ucode) > 0:
                out=out+('&#'+ucode+';')
            else:
                out=out+('@')
            continue
        if md.startswith("/*"):
            while not md.startswith("*/"):
                md=md[1:]
            md=md[2:]
            continue
        if md.startswith("=#="):
            bold=0
            size="medium"
            isHeading=False
            md=md[3:]
            createspan()
            continue
        if md.startswith("######"):
            isHeading=True
            size="0.75em"
            bold=1
            md=md[6:]
            createspan()
            continue
        if md.startswith("#####"):
            isHeading=True
            size="0.83em"
            bold=1
            md=md[5:]
            createspan()
            continue
        if md.startswith("####"):
            isHeading=True
            size="1em"
            bold=1
            md=md[4:]
            createspan()
            continue
        if md.startswith("###"):
            isHeading=True
            size="1.17em"
            bold=1
            md=md[3:]
            createspan()
            continue
        if md.startswith("##"):
            isHeading=True
            size="1.5em"
            bold=1
            md=md[2:]
            createspan()
            continue
        if md.startswith("#"):
            isHeading=True
            size="2em"
            bold=1
            md=md[1:]
            createspan()
            continue
        # if md[0]=='|'and len(md)>2 and md[2]=='|':
        #     if md[1]=='<': align='left'
        #     if md[1]=='^': align='center'
        #     if md[1]=='>': align='right'
        #     if md[1]=='=': align='justify'
        #     md=md[3:]
        #     createspan()
        #     continue
        if md.startswith("<{<("):
            md=md[4:]
            while md[0] is not ")":
                imageUrl=imageUrl+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                imageAlt=imageAlt+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not "}":
                link=link+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                linkText=linkText+md[0]
                md=md[1:]
            md=md[1:]
            out=out+('      <a href="'+link+'"><img src="'+imageUrl+'" alt="'+imageAlt+'" style="width:30%" title="'+imageAlt+'" style="'+styleContent+'" /></a>')
            link=''
            linkText=''
            imageAlt=''
            imageUrl=''
            createspan()
            continue
        if md.startswith("<(<{"):
            md=md[4:]
            while md[0] is not "}":
                link=link+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                linkText=linkText+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ")":
                imageUrl=imageUrl+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                imageAlt=imageAlt+md[0]
                md=md[1:]
            md=md[1:]
            out=out+('      <a href="'+link+'"><img src="'+imageUrl+'" alt="'+imageAlt+'" style="width:30%" title="'+imageAlt+'" style="'+styleContent+'" /></a>')
            link=''
            linkText=''
            imageAlt=''
            imageUrl=''
            createspan()
            continue
        if md.startswith("<["):
            md=md[2:]
            while md[0] is not "]":
                styleContent=styleContent+md[0]
                md=md[1:]
            md=md[1:]
            createspan()
            while md[0] is not ">":
                out=out+(md[0])
                md=md[1:]
            md=md[1:]
            styleContent=''
            createspan()
            continue
        if md.startswith("<{"):
            md=md[2:]
            while md[0] is not "}":
                link=link+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                linkText=linkText+md[0]
                md=md[1:]
            md=md[1:]
            out=out+('      <a href="'+link+'">'+linkText+'</a>')
            link=''
            linkText=''
            createspan()
            continue
        if md.startswith("<("):
            md=md[2:]
            while md[0] is not ")":
                imageUrl=imageUrl+md[0]
                md=md[1:]
            md=md[1:]
            while md[0] is not ">":
                imageAlt=imageAlt+md[0]
                md=md[1:]
            md=md[1:]
            out=out+('      <img src="'+imageUrl+'" alt="'+imageAlt+'" style="width:30%" title="'+imageAlt+'" style="'+styleContent+'" />')
            imageAlt=''
            imageUrl=''
            createspan()
            continue
        if md.startswith("3---"):
            md=md[4:]
            out=out+('      <div style="width: 80%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("2---"):
            md=md[4:]
            out=out+('      <div style="width: 90%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("1---"):
            md=md[4:]
            out=out+('      <div style="width: 100%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("4---"):
            md=md[4:]
            out=out+('      <div style="width: 70%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("5---"):
            md=md[4:]
            out=out+('      <div style="width: 60%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("6---"):
            md=md[4:]
            out=out+('      <div style="width: 50%; background-color: '+color+'; margin-left: '+('0','10','10','20')[('left','center','justify','right').index(align)]+'%; height: 2px;"></div>\n')
            continue
        if md.startswith("**"):
            if bold==0:
                bold=1
            else:
                bold=0
            md=md[2:]
            createspan()
            continue
        if md.startswith("*"):
            if style==1: style=0
            else: style=1
            md=md[1:]
            createspan()
            continue
        if md.startswith("__"):
            if line==1: line=0
            else: line=1
            md=md[2:]
            createspan()
            continue
        if md.startswith("~"):
            if line==2: line=0
            else: line=2
            md=md[1:]
            createspan()
            continue
        if md.startswith("%%"):
            if line==3: line=0
            else: line=3
            md=md[2:]
            createspan()
            continue
        if md.startswith("<--"):
            out=out+('<span>&#8592;</span>')
            md=md[3:]
            createspan()
            continue
        if md.startswith("-->"):
            out=out+('<span>&#8594;</span>')
            md=md[3:]
            createspan()
            continue
        if md.startswith("<->"):
            out=out+('<span>&#8596;</span>')
            md=md[3:]
            createspan()
            continue
        if md.startswith("[["):
            isHtml=True
            md=md[2:]
            createspan()
            continue
        if md.startswith("]]"):
            isHtml=False
            md=md[2:]
            createspan()
            continue
        if md.startswith("`"):
            if isCode==False:
                cssCodeClass='class=code '
                isCode=True
            else:
                cssCodeClass=''
                isCode=False
            md=md[1:]
            createspan()
            continue
        if md[0]=='>':
            if isHtml==True:
                out=out+('>')
            else:
                out=out+('&gt;')
            md=md[1:]
            continue
        if md[0]=='<':
            if isHtml==True:
                out=out+('<')
            else:
                out=out+('&lt;')
            md=md[1:]
            continue
        if md[0]=='&':
            out=out+('&amp;')
            md=md[1:]
            continue
        if md[0]=='+':
            out=out+("&bull; ")
            md=md[1:]
        if md.startswith("(c)"):
            out=out+("&copy;")
            md=md[3:]
        if md.startswith("(tm)"):
            out=out+("&trade;")
            md=md[4:]
        if md.startswith(";;"):
            if isHeading==True:
                bold=0
                size="medium"
                isHeading=False
            out=out+('<br />')
            md=md[2:]
            createspan()
            continue
        if md.startswith("  "):
            if isHeading==True:
                bold=0
                size="medium"
                isHeading=False
            out=out+('<br />')
            md=md[2:]
            createspan()
            continue
        out=out+(md[0])
        md=md[1:]
    out=out+('</span>')
    out=out+("""
        </body>
    </html>""")
    return out
def prnt(md, title):
    sys.stdout.write(run(md, title))
    sys.stdout.flush()
