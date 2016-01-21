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
from TrialHandler3 import TrialHandler3
from pupil_support import *

mouse_on=False
dim_x=dim_y=800
fullscr=True

# TIMES
FIXATION=1
PRESENTATION=1

colors=['green','blue','white', 'red', 'gold', 'Purple']

# TRIAL TYPES
CTRL=0
CW=1
CCW=2

IN=3
OUT=4


def exit_task():
    core.quit()

def toCar(r,deg):
    x=r*math.cos(math.radians(deg))
    y=r*math.sin(math.radians(deg))
    return (x,y)

def getAngle(v):
    a=math.atan2(v[1],v[0])
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


v_tr=0.5


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

        # calculate number of R,Angle pair that we have - minus first 2 columns, Delay and Type
        n_stim = (len(line) - 2) / 2

        delay=line[0]
        type=line[1]
        stims=[]
        for n in range(0,n_stim):
            ring=float(line[2+n*2])
            angle=float(line[3+n*2])
            stims+=[(ring,angle)]

        stimList.append( 
        {'delay':float(delay), 'type':float(type), 'stims': stims})   

    stim_input.close()
    #organise the trials 
    trials = TrialHandler3(trial_list = stimList,subject_name=subject_name)

    pupil = Pupil(log_path=trials.log_path,v_tr=v_tr)
    pupil_on = pupil.test_pupil()

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

    if pupil_on: pupil.record_start()

    while not trials.empty():
        
        thisTrial = trials.next_trial()
        ts_b = time()
        delay=thisTrial['delay']
        stims_objs=[]

        shuffle(colors)

        
        for n  in range(len(thisTrial['stims'])):
            r,angle = thisTrial['stims'][n]
            color=colors[n]

            if r == -1 or angle == -1: # code for unvisitble stims
                color = mywin.color
        
            x,y=toCar(r,angle)
            stim = visual.PatchStim(win=mywin,size=0.8, mask='circle',pos=[x,y], sf=0,color=color,units='cm')
            stims_objs.append(stim)


        # SYNC PERIOD
        fixation = visual.PatchStim(win=mywin, mask='gauss', size=0.5, pos=[0,0], sf=0, color='black')
        fixation.draw()
        mywin.update()

        mouse.clickReset()
        while mouse.getPressed()[0]==0:
            #wait for a button to be pressed
            pass
        
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
        
        # #wait for mouse button to get release
        # while mouse.getPressed()[0]==1:
        #     pass
        
        if event.getKeys("escape"): exit_task()
        
        # FIXATION PERIOD
        t=0
        trialClock.reset()
        ts_f = time()

        fixation.draw()
        mywin.flip()
        sleep(0.1) # give 100ms for the subject to refixate

        if pupil_on: pupil.detect_sacc_start()

        while t<FIXATION:
            if not pupil.fixated.value:
                break
            fixation.draw()
            mywin.flip()
            t=trialClock.getTime()    

      
        # STIMULUS PRESENTATION PERIOD
        t=0
        trialClock.reset()
        ts_p = time()
        while t<PRESENTATION:
            if not pupil.fixated.value:
                break
            if event.getKeys("escape"): exit_task()
            fixation.draw()
            map(lambda x: x.draw(),stims_objs)
            mywin.flip()
            t=trialClock.getTime()
       
        # DELAY PERIOD
        t=0
        trialClock.reset()
        ts_d=time()
        while t<delay:
            if not pupil.fixated.value:
                break
            if event.getKeys("escape"): exit_task()
            fixation.draw()
            mywin.flip()
            t=trialClock.getTime()

        trials.add_data('fixated', pupil.fixated.value)

        if not pupil.fixated.value:
            trials.repeat_trial(thisTrial)
            if pupil_on: pupil.detect_sacc_stop()
            say_msg("Please, fixate on the center of the screen",2,mywin)
            continue

        if pupil_on: pupil.detect_sacc_stop()
      
        # RESPONDE PERIOD
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

        stim1 = stims_objs[0]
        (r,angle) = thisTrial["stims"][0]
        ts_e = time()
        mtime = trialClock.getTime()
        choice_pos=stim1.pos - pos
        choice_angle=getAngle(stim1.pos) - getAngle(pos)
        choice_R=r - norm(pos)
        
     
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

    if pupil_on: pupil.record_stop()
    
    map(lambda x: x.clearTextures(),stims_objs)
    fixation.clearTextures()
    mywin.flip()

    say_msg("Thank you!",2,mywin)
    

    print "Experiment duration:",totalClock.getTime()

    #clean up
    event.clearEvents()
    mywin.close()
    #exit_task()
        
