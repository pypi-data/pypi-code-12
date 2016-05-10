from puck import Puck, api_response, request


app = Puck()


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return api_response(
            data={
                'test' : 'hello world!'
            }
        )
    elif request.method == 'POST':
        print '---------'
        # print request.environ['CONTENT_LENGTH']
        # print request.environ['wsgi.input'].read(67958)
        print request.file
        print 'set 0'
        file = request.file[0][1]
        print 'set 1'
        file_ = request.file[1][1]
        print 'set 2'
        # for d in read_in_chunks(file.stream):
        #     print d
        file.create('/Users/Eric/hahahaha.md')
        print 'finish 1'
        file_.create('/Users/Eric/heihei.py')
        print 'finish'
        # print request.file[0]
        return request.file


@app.route('/<name>')
def hello_name(name):
    return 'hello, %s' % name
