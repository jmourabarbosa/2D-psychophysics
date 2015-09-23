from psychopy import * #import all libraries from PsychoPy
import math
import scipy
import sys
from random import randrange,choice,shuffle
from numpy.linalg import norm
from pickle import dump
import zmq
import numpy as np
from multiprocessing import Process, Value,Array
from time import sleep,time
from random import randrange
from TrialHandler2 import TrialHandler2

mouse_on=False
dim_x=dim_y=800
fullscr=False

p_dir = "subjects"

# TIMES
FIXATION=1
PRESENTATION=1

colors=['green','blue','white', 'red', 'gold']


#Pupil network setup
port = "5000"
localhost="tcp://127.0.0.1:"


def test_pupil():

    def test_pupil_aux():

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(localhost+port)
        socket.setsockopt(zmq.SUBSCRIBE, '')

        msg = socket.recv()
        print "msg",msg

    p=Process(target=test_pupil_aux)
    p.start()
    sleep(0.1)


    if p.is_alive():
        p.terminate()
        return False

    return True

def read_pupil(finish):
    pupil_data=[]
    gaze_data=[]
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(localhost+port)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    n_frame=0

    while not finish.value:
        msg = socket.recv()
        items = msg.split("\n") 
        msg_type = items.pop(0)   
        if msg_type == 'Pupil':
            pupil_data+=items

        else:
            gaze_data+=items

    p_fid = open('pupil.pickle','w')
    g_fid = open('gaze.pickle','w')

    dump(pupil_data,p_fid)
    dump(pupil_data,g_fid) 
    p_fid.close()
    g_fid.close()  

def get_frame(socket):

    msg = socket.recv()
    items = msg.split("\n")
    msg_type = items.pop(0)

    msg = socket.recv()
    items = msg.split("\n")
    msg_type = items.pop(0)

    return items

def detect_sacc(v_tr):

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(localhost+port)
    socket.setsockopt(zmq.SUBSCRIBE, 'Gaze')

    vel=[]
    n_sacc=0
    while detect.value:
        n = 0
        times=[0,0]
        points = [0,0]
        while n<2:
            items = get_frame(socket)
            times[n]=float(items[-2].split(":")[1])
            point = items[0].split(":")
            x=point[1].split(",")[0][1:]
            y=point[1].split(",")[1][:-1]
            points[n]=(float(x),float(y))
            n+=1
    
        (x1,y1) = points[0]
        (x2,y2) = points[1]
        v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
        #print v, v_tr
    
        if v > v_tr:
            n_sacc+=1
            print "saccade: ",n_sacc,v
            fixated.value=0
            vel.append(v)

def detect_sacc_start(detector):
    detect.value=True
    detector[0].start() 

def detect_sacc_stop(detector):
    detect.value=False
    detector[0] = Process(target=detect_sacc, args=(v_tr,))
    fixated.value=1


def exit_task():
    finish.value=1
    sleep(0.1)
    core.quit()

def toCar(r,deg):
    x=r*math.cos(math.radians(deg))
    y=r*math.sin(math.radians(deg))
    return (x,y)

def getAngle(v):
    a=math.atan2(v[0],v[1])
    return 180*a/math.pi

def say_msg(message,duration,win):

    msgClock=core.Clock()
    msgText=visual.TextStim(win=win, ori=0,
        text=message,
        pos=[0,0], height=1.5,
        rgb=[1, 1, 1])

    t=0
    msgClock.reset()
    while t<duration:
        t=msgClock.getTime()            
        msgText.draw()
        win.flip()


finish = Value('i',0)
detect = Value('i',0)
fixated = Value('i',1)
v_tr=0.5

record=Process(target=read_pupil,args=(finish,))
detector=[Process(target=detect_sacc, args=(v_tr,))]


if __name__ == "__main__":

    info = {'Velocity threshold':'0.5'}
    infoDlg = gui.DlgFromDict(dictionary=info, title='WM experiment')
    if infoDlg.OK:
        v_tr=float(info['Velocity threshold'])
    if infoDlg.OK==False: core.quit() #user pressed cancel


    info = {'Subject':'Subject_1'}
    infoDlg = gui.DlgFromDict(dictionary=info, title='WM experiment')
    if infoDlg.OK:
        subject_name=info['Subject']
    if infoDlg.OK==False: core.quit() #user pressed cancel

    mywin = visual.Window([dim_x, dim_y],monitor="testMonitor", fullscr=fullscr, units="cm") #create a window full screen
    mouse=event.Mouse(win=mywin)
    mouse.setVisible(mouse_on)

    stim_input=open(sys.argv[1],'r')
    lines=stim_input.readlines()[1:]
    stimList = []


    for line in lines:
        line = line.split()
        delay=line[0]
        type=line[1]
        ring1=line[2]
        angle1=line[3]
        ring2=line[4]
        angle2=line[5]
        ring3=line[6]
        angle3=line[7]

        stimList.append( 
        {'delay':float(delay), 'type':float(type), 'angle1':float(angle1),'ring1':float(ring1),
        'angle2':float(angle2),'ring2':float(ring2),'angle3':float(angle3),'ring3':float(ring3)})   

    stim_input.close()
    #organise the trials 
    trials = TrialHandler2(trial_list = stimList,subject_name=subject_name)

    trials.add_type('choice_x')
    trials.add_type('choice_y')
    trials.add_type('fixated')
    trials.add_type('choiceAngle')
    trials.add_type('choiceR')
    trials.add_type('RT')# reaction time
    trials.add_type('MT')# movement time
    trials.add_type('ts_b')# timestamp begin trial
    trials.add_type('ts_f')# timestamp begin fixation
    trials.add_type('ts_p')# timestamp begin presentation
    trials.add_type('ts_d')# timestamp begin delay
    trials.add_type('ts_r')# timestamp begin response
    trials.add_type('ts_e')# timestamp end

    #start the trials
    trialClock = core.Clock()
    totalClock = core.Clock()

    totalClock.reset()
    pupil=test_pupil()

    if pupil: record.start()

    while not trials.empty():
        thisTrial = trials.next_trial()

        ts_b = time()
        # sync period
        fixation = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[0,0], sf=0, color='black')
        fixation.draw()
        mywin.update()

        mouse.clickReset()
        while mouse.getPressed()[0]==0:
            pass#wait for a button to be pressed
        
        x,y=mouse.getPos()
        while not ( abs(x) < 0.5 and abs(y) < 0.5):
            if event.getKeys("escape"): exit_task()
            x,y=pos=mouse.getPos()
            resp = visual.PatchStim(win=mywin, size=0.5, pos=pos, sf=0, color='black')
            resp.draw()
            fixation.draw()
            mywin.update()
        
        fixation = visual.PatchStim(win=mywin, size=0.5, pos=[0,0], sf=0, color='black')
        fixation.draw()
        mywin.update()
        
        #wait for mouse button to get release
        while mouse.getPressed()[0]==1:
            pass
        
        if event.getKeys("escape"): exit_task()

        shuffle(colors)
        color=colors[0]
        r=thisTrial['ring1']
        x,y=toCar(r,thisTrial['angle1'])
        stim1 = visual.PatchStim(win=mywin,size=0.8, mask='circle',pos=[x,y], sf=0,color=color,units='cm')
            
        color=colors[1]
        r=thisTrial['ring2']
        x,y=toCar(r,thisTrial['angle2'])
        stim2 = visual.PatchStim(win=mywin, size=0.8, mask='circle',pos=[x,y], sf=0,color=color,units='cm')
        
        color=colors[2]
        r=thisTrial['ring3']
        x,y=toCar(r,thisTrial['angle3'])
        stim3 = visual.PatchStim(win=mywin, size=0.8, mask='circle',pos=[x,y], sf=0,color=color,units='cm')
        
        #delay period
        delay=thisTrial['delay']
        
        #start the trial with fixation
        t=0
        trialClock.reset()
        ts_f = time()

        fixation.draw()
        mywin.flip()
        sleep(0.1) # give 100ms for the subject to refixate

        if pupil: detect_sacc_start(detector)

        while t<FIXATION:
            if not fixated.value:
                break
            fixation.draw()
            mywin.flip()
            t=trialClock.getTime()    

      
        #draw the stimuli and update the window for the duration of stimulus presentation
        t=0
        trialClock.reset()
        ts_p = time()
        while t<PRESENTATION:
            if not fixated.value:
                break
            if event.getKeys("escape"): exit_task()
            fixation.draw()
            stim2.draw()
            stim3.draw()
            stim1.draw()
            mywin.flip()
            t=trialClock.getTime()
       
        #delay period
        t=0
        trialClock.reset()
        ts_d=time()
        while t<delay:
            if not fixated.value:
                break
            if event.getKeys("escape"): exit_task()
            fixation.draw()
            mywin.flip()
            t=trialClock.getTime()

        trials.add_data('fixated', fixated.value)

        if not fixated.value:
            trials.repeat_trial(thisTrial)
            if pupil: detect_sacc_stop(detector)
            say_msg("Please, fixate on the center of the screen",2,mywin)
            continue

        if pupil: detect_sacc_stop(detector)
      
        #response period
        choice_trial=0
        event.clearEvents()
        fixation.setColor(colors[0])
        fixation.draw()
        mywin.update()
        ts_r = time()

        #reaction time
        trialClock.reset()
        mouse.clickReset()
        while mouse.getPressed()[0]==0:
            pass#wait for a button to be pressed
        rtime = trialClock.getTime()
        
        #movement time
        trialClock.reset()
        #keep waiting for the release
        while mouse.getPressed()[0]==1:
            pos=mouse.getPos()
            resp = visual.Circle(mywin,radius=0.3,pos=pos)
            resp.setFillColor(colors[0])
            resp.draw()
            fixation.draw()
            mywin.update()
            pass

        ts_e = time()
        mtime = trialClock.getTime()
        choice_pos=stim1.pos - pos
        choice_angle=getAngle(pos)-getAngle(stim1.pos)
        choice_R=norm(pos)-(thisTrial['ring1']*2+6)
        
     
        trials.add_data('choice_x', choice_pos[0])
        trials.add_data('choice_y', choice_pos[1])
        trials.add_data('choiceAngle', choice_angle)
        trials.add_data('choiceR', choice_R)
        trials.add_data('RT', rtime)
        trials.add_data('MT', mtime)
        trials.add_data('ts_b',ts_b)
        trials.add_data('ts_f',ts_f)
        trials.add_data('ts_p',ts_p)
        trials.add_data('ts_d',ts_d)
        trials.add_data('ts_r',ts_r)
        trials.add_data('ts_e',ts_e)
       
        resp = visual.Circle(mywin,radius=0.3,pos=pos)
        resp.setFillColor('red')
        resp.draw()


    trials.save_log()
    finish.value=1

    if pupil: record.join()



    stim1.clearTextures()
    stim2.clearTextures()
    stim3.clearTextures()
    fixation.clearTextures()
    mywin.flip()

    say_msg("Thank you!",2,mywin)
    

    print "Experiment duration:",totalClock.getTime()

    #clean up
    event.clearEvents()
    mywin.close()
    #exit_task()
        
