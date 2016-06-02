from flask import Flask, request
import flask
import MoshinSomeStuff
#print 'create flask app ',__name__
#app = Flask(__name__)
app = Flask('MoshMosh')

@app.route('/HOMEPAGE', methods=['GET'])
def typechoose():
    '''Displays mosh type selections (overlay,shmear,bloom), get request transfers to respective URL based on selection.'''
    fileObject = file('GifBreakerUI_homepage.html','r')
    output  = fileObject.read()
    fileObject.close()
    return output

@app.route('/BLOOM', methods=['GET'])
def bloom ():
    '''Display settings for bloom and asks for user input (oldFileName,newFilenName,wait,moshDurationl,moshType=bloom). Post request selections to (/FINAL)'''
    fileObject = file('GifBreakerUI_Bloom.html','r')
    output  = fileObject.read()
    fileObject.close()
    return output
@app.route('/SHMEAR', methods=['GET'])
def shmear ():
    '''Display settings for shmear and asks for user input (oldFileName,newFileName,moshType=shmear). Post request selections to (/FINAL)'''
    fileObject = file('GifBreakerUI_Shmear.html','r')
    output  = fileObject.read()
    fileObject.close()
    return output

@app.route('/OVERLAY', methods=['GET'])
def overlay ():
    '''Display settings for overlay and asks for user input (oldFileName,newFileName,moshType=overlay). Post request selections to (/FINAL)'''
    fileObject = file('GifBreakerUI_Overlay.html','r')
    output  = fileObject.read()
    fileObject.close()
    return output

@app.route('/FINAL', methods=['GET', 'POST'])
def final ():
    '''Recieves posts from previous forms (/BLOOM, /OVERLAY, /SHMEAR), inputs (oldFileName,newFilenName,wait,moshDurationl,moshType=x) makes a post request with that info to sent to back end. Makes a get request to recieve finished product from back end. Displays download link for moshed file received through get request.'''
    #return None
    f1 = request.files['file1']
    fileObject= file('upload1.avi','wb')
    fileObject.write(f1.read())
    fileObject.close()
    if request.form['moshtype'] == 'overlay':
        f2 = request.files['file2']
        fileObject=file('upload2.avi','wb')
        fileObject.write(f2.read())
        fileObject.close()
        MoshinSomeStuff.overlay('upload1.avi','upload2','youroverlay.avi')
        return flask.send_file('youroverlay.avi')
    elif request.form['moshtype'] == 'bloom':
        duration= int(request.form['duration'])
        wait = int(request.form['wait'])
        MoshinSomeStuff.bloom('upload1.avi','yourbloom.avi',wait,duration)
        return flask.send_file('yourbloom.avi')
    elif request.form['moshtype'] == 'shmear':
        MoshinSomeStuff.shmear('upload1.avi','yourshmear.avi')
        return flask.send_file('yourshmear.avi')
    
    
#"Hello World I'm in debug mode" + request.form['duration'] +request.form['moshtype']
    
#+'of type:'+str(type(request.form['file']))+':'+'with properties:'+str(dir(request.form['file']))
def do_run ():
    #app.run(debug=True)
    app.run()

if __name__ == '__main__':
    app.run(debug=True)
