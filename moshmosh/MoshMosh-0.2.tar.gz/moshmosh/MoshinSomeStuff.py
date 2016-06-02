from pymosh import Index
from pymosh.mpeg4 import is_iframe
import sys
import os
from visvis.vvmovie import images2avi as vv
from PIL import Image
import cv2

def count_frames(index):
    '''Returns the number of frames in an avi, given an Index based on the avi'''
    number_of_frames = 0
    for stream in index.video:
        for i in stream:
            number_of_frames += 1
    return number_of_frames

def find_image_size(filename):
    '''Returns the dimensions of an avi, given the avi'''
    images = vv.readAvi(filename, False)
    image = images[0]
    return image.size

def write_shell(length, duration, size):
    '''Writes an avi containing only black frames of the intended final dimensions, frame length, and frame duration'''
    frames = []
    for i in range(length):
        frames.append(Image.new("RGB",size))
    vv.writeAvi("shell.avi", frames, duration)

def process_frame(frame, buf):
    '''Determines if given frame is a p-frame or an i-frame.  If it is an i-frame, the buffer stays the same and it returns the frame held in the buffer.  If it is a p-frame, it replaces the buffer with the frame, and returns the frame.'''
    #if there is no frame in buf or the frame is not i-frame
    if buf[0] == None or not is_iframe(frame):
        #then buf is the seen p-frame 
        buf[0] = frame 
    else:
        #if it IS an iframe then use the buf'ers pframe
        frame = buf[0]
        #return the frame
    return frame

def find_framerate(filename):
    '''Given an avi, finds the framerate of the avi'''
    #if __name__ == '__main__' :
 
    video = cv2.VideoCapture(filename);
     
        # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
     
    if int(major_ver)  < 3 :
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
        return float(fps)
    else :
        fps = video.get(cv2.CAP_PROP_FPS)
        return float(fps)
    
    video.release();

def find_frame_duration(filename):
    '''Converts the framerate from find_framerate into a frame duration'''
    duration = 1/find_framerate(filename)
    return duration


def bloom(old_filename, new_filename, wait, bloom):
    '''Creates an avi that behaves normally for (wait) frames, copies the frame after the wait for (bloom) frames, and then continues normally until the end of the avi''' 
    f = Index(old_filename) #Allows original avi to be accessed by pymosh
    write_shell(count_frames(f)+bloom, find_frame_duration(old_filename), find_image_size(old_filename)) #Creates a blank avi to be written into

    buf = [None] #Stores most recent p-frame, to be used when processing frames
    
    g = Index("shell.avi") #Allows the shell avi to be written into by pymosh
    for stream in f.video: #Puts the frames from the old avi in the desired order in newstream
        newstream = []
        newstream.append(stream[0])
        ix = 0
        for i in stream[1:]:
            ix+=1
            newstream.append(process_frame(stream[ix], buf))
            if ix == wait:
                for i in range(bloom):
                    newstream.append(newstream[-1])
        for gstream in g.video: #Replaces shell's black frames with old avi's frames
            gstream.replace(newstream)
    g.rebuild()
    g.write(new_filename) #Writes final avi
    os.remove(os.getcwd() + "/shell.avi") #Deletes shell avi created by write_shell

def shmear(old_filename, new_filename):
    '''Creates an avi with each of the P-frames doubled.'''
    f = Index(old_filename) #Allows original avi to be accessed by pymosh
    write_shell(count_frames(f)*2-1, find_frame_duration(old_filename), find_image_size(old_filename)) #Creates a blank avi to be written into

    buf = [None] #Stores most recent p-frame, to be used when processing frames

    g = Index("shell.avi") #Allows the shell avi to be written into by pymosh
    for stream in f.video: #Puts each motion frame from the old avi twice into the new avi
        newstream = []
        newstream.append(stream[0])
        ix = 0
        for i in stream[1:]:
            ix+=1
            newstream.append(process_frame(stream[ix], buf))
            newstream.append(process_frame(stream[ix], buf))
        for gstream in g.video: #Replaces shell's black frames with old avi's frames
            gstream.replace(newstream)
    g.rebuild()
    g.write(new_filename) #Writes final avi
    os.remove(os.getcwd() + "/shell.avi") #Deletes shell avi created by write_shell

def overlay(old_filename_1, old_filename_2, new_filename):
    '''Creates an avi where the motion of old_filename_2 is layed over old_filename_1'''
    size = find_image_size(old_filename_1)
    if size != find_image_size(old_filename_2): #If the avi's have different dimensions, send an error and terminate function
        return 'Please only overlay gifs of the same dimensions'
    e = Index(old_filename_1) #Allows first old avi to be accessed by pymosh
    f = Index(old_filename_2) #Allows second old avi to be accessed by pymosh
    write_shell(count_frames(e)+count_frames(f), find_frame_duration(old_filename_1), size) #Creates a blank avi to be written into

    buf = [None] #Stores most recent p-frame, to be used when processing frames

    g = Index("shell.avi") #Allows the shell avi to be written into by pymosh
    newstream = [] #A list to store frames in, is later turned into the final avi
    for stream in e.video: #Puts all of first avi's frames into newstream, processing each frame
        newstream.append(process_frame(stream[0], buf))
        ix = 0
        for i in stream[1:]:
            ix+=1
            newstream.append(process_frame(stream[ix], buf))
    for stream in f.video: #Puts all of second avi's frames into newstream, processing each frame
        ix = 0
        for i in stream:
            newstream.append(process_frame(stream[ix], buf))
            ix+=1
    for stream in g.video: #Replaces shell's black frames with old avi's frames
        stream.replace(newstream)
    g.rebuild()
    g.write(new_filename) #Writes final avi
    os.remove(os.getcwd() + "/shell.avi") #Deletes shell avi created by write_shell

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: {0} interval filename'.format(sys.argv[0])
        sys.exit(1)

''' try:
        wait = int(sys.argv[3])
        if wait < 2:
            raise ValueError
    except ValueError:
        print 'Interval must be an integer >= 2.'
        sys.exit(1)'''

##overlay(sys.argv[1], sys.argv[2], (sys.argv[3]))
#shmear(sys.argv[1], sys.argv[2])
        
