from PIL import Image, ImageDraw
from itertools import product

def load_image(src, times=1):
    """画像ファイルの読込み"""
    from urllib.request import urlopen
    from collections import Counter
    from random import seed, shuffle
    with urlopen(src) if src.startswith('http') else open(src, 'rb') as fd:
        im = Image.open(fd).convert('RGB')
    # 代表色(最も使用頻度の多い色)を抽出
    cc = sorted([(v, k) for k, v in Counter(im.getdata()).items()])[-1][1]
    # RGB=(0,1,?)の色をなくす
    for y, x in product(range(im.height), range(im.width)):
        R, G, B = im.getpixel((x, y))[:3]
        if (R, G) == (0, 1):
            im.putpixel(0, 0, B)
    # 代表色のエリアをRGB=(0,1,通し番号)で塗りつぶす
    n = 0
    for y, x in product(range(im.height), range(im.width)):
        if im.getpixel((x, y)) != cc:
            continue
        ImageDraw.floodfill(im, (x, y), (0, 1, n))
        n += 1
    # 境界を少し広げる
    seed(1)
    dd = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    for h in range(times):
        l = list(product(range(1, im.height-1), range(1, im.width-1)))
        shuffle(l)
        for y, x in l:
            c = im.getpixel((x, y))
            if c[:2] == (0, 1):
                for i, j in dd:
                    if im.getpixel((x+i, y+j))[:2] != (0, 1):
                        im.putpixel((x+i, y+j), c)
    return im

def make_graph(im):
    """グラフ作成"""
    import networkx as nx
    g = nx.Graph()
    for y, x in product(range(im.height-1), range(im.width-1)):
        c1 = im.getpixel((x, y))
        if c1[:2] != (0, 1):
            continue
        c2 = im.getpixel((x+1, y))
        c3 = im.getpixel((x, y+1))
        if c2[:2] == (0, 1) and c1[2] != c2[2]:
            g.add_edge(c1[2], c2[2])
        if c3[:2] == (0, 1) and c1[2] != c3[2]:
            g.add_edge(c1[2], c3[2])
    return g

def solve_four_color(im, g):
    """4色問題を解く"""
    from pulp import LpProblem, LpVariable, LpBinary, lpSum, lpDot, value
    r4 = range(4)
    m = LpProblem() # 数理モデル
    # エリアiを色jにするかどうか
    v = {i:[LpVariable('v%d_%d'%(i, j), cat=LpBinary) for j in r4] for i in g.nodes()}
    for i in g.nodes():
        m += lpSum(v[i]) == 1
    for i, j in g.edges():
        for k in r4:
            m += v[i][k] + v[j][k] <= 1
    m.solve()
    co = [(97, 132, 219), (228, 128, 109), (255, 241, 164), (121, 201, 164)] # 4色
    rr = {k:int(value(lpDot(r4, w))) for k, w in v.items()} # 結果
    for y, x in product(range(im.height-1), range(im.width-1)):
        c = im.getpixel((x, y))
        if c[:2] == (0, 1) and c[2] in rr: # エリアならば、結果で塗る
            ImageDraw.floodfill(im, (x, y), co[rr[c[2]]])

if __name__ == '__main__':
    from os import environ, path
    from flask import Flask, redirect, request, make_response
    from werkzeug import secure_filename
    app = Flask(__name__)
    @app.route('/', methods=['GET', 'POST'])
    def root():
        if request.method != 'POST':
            return ("<form action='/' enctype='multipart/form-data' "
                "method='POST'><input type='file' name='im' size='30'>"
                "<input type='submit' value='send'></from>")
        f = request.files['im']
        fn = secure_filename(f.filename) if f else ''
        ext = path.splitext(fn)[1]
        if not fn or not ext.endswith(('png', 'gif', 'jgp', 'jpeg')):
            return redirect('/')
        fn = 'fig' + ext
        f.save(fn)
        im = load_image(fn)
        g = make_graph(im)
        solve_four_color(im, g)
        im.save(fn)
        res = make_response()
        with open(fn, 'rb') as fp:
            res.data = fp.read()
        res.headers['Content-Type'] = 'application/octet-stream'
        res.headers['Content-Disposition'] = 'attachment; filename=fig'+ext
        return res
    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    PORT = environ.get('SERVER_PORT', '')
    PORT = int(PORT) if PORT.isdigit() else 8888
    app.config['MAX_CONTENT_LENGTH'] = 210000
    app.debug = True
    app.run(HOST, PORT)
