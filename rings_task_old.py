from psychopy import * #import all libraries from PsychoPy
import math
import scipy
import sys
from random import randrange,choice,shuffle
from numpy.linalg import norm
from pickle import dump
import os
import zmq
import numpy as np
from multiprocessing import Process, Value,Array
from time import sleep,time
from hashlib import md5
from random import randrange
		
p_dir = "subjects"

# TIMES
FIXATION=1
PRESENTATION=1

colors=['green','blue','white']


#Pupil network setup
port = "5000"
localhost="tcp://127.0.0.1:"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(localhost+port)
socket.setsockopt(zmq.SUBSCRIBE, '')

finish = Value('i',0)
detect = Value('i',0)
fixated = Value('i',1)

discarded = []
blacklist = []

class TrialList(object):
     def __init__(self, data_dict=[], trial_list=[],subject_name='subject_name',pdir='subjects'):
        """Return a Customer object whose name is *name* and starting
        balance is *balance*."""
        self.data_dict = {}
        self.trial_list = trial_list
        self.next_trial = 0
        self.n_trials = len(trial_list)
        self.subject = subject_name
        self.dir = pdir
        n=0
        while os.path.exists(pdir+"/"+self.subject_name): 
            n+=1
        self.log_path=self.pdir+"/"+self.subject+"_"+srt(n)
    
    def add_data(key):
        self.data_dict[key]=[]
    
    def add(key,data):
        self.data[key].append(data)

    def  empty():
        return sel.n_trials<self.next_trial+1

    def next_trial():

        trial = self.trial_list[self.next_trial]
        self.next_trial+=1
        return trial

    # Assumies logging of repetition reason is done inside the main loop
    def repeat_trial(trial):

        if self.empty():
            return False

        # There is just on more trial, apend at the end
        if self.next_trial == self.n_trials - 1: 
            self.trial_list.append(trial)
            return True

        # Generate random position, except the next trial
        new_pos = randrange(self.next_trial+1,self.n_trials)
        self.trial_list.insert(new_pos,trial)
        return True

    def save_log():
        # Think about padding the data when it wasn't logged!

        if not os.path.isdir(self.log_path):
            os.makedirs(p_dir)

        # How data will appear: tab delim and 2 decimals
        form_stims = "\t".join(['%.2f']*len(self.stimList[0]) )
        form_data = "\t".join(['%.2f']*len(self.data))

        header = "\t".join(self.stimList[0].keys() + self.data_dict.keys())

        body_stims = [form_stims % tuple(t.values()) for t in self.trial_list]
        body_data  = [form_data % tuple(data) for t in self.data.values]

        print header
        print body_stims, body_data






class TrialHandler2(data.TrialHandler):
	def next2(self):
		idx = range(1,len(self.trialList))
        	self.trialList += [self.trialList[self.thisIndex]]
		self.sequenceIndices = np.vstack((self.sequenceIndices,self.sequenceIndices[self.thisTrialN]))
		self.thisTrialN-=1

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

	#dump(p_fid,pupil_data)
	#dump(g_fid,pupil_data)
	

def get_frame():
	msg = socket.recv()
        items = msg.split("\n")
        msg_type = items.pop(0)

	while msg_type != "Gaze":
		msg = socket.recv()
	        items = msg.split("\n")
        	msg_type = items.pop(0)
	return items

def detect_sacc(v_tr):
	vel=[]
	n_sacc=0
	while detect.value:
		n = 0
		times=[0,0]
		points = [0,0]
		while n<2:
			items = get_frame()
			times[n]=float(items[-2].split(":")[1])
			point = items[0].split(":")
			x=point[1].split(",")[0][1:]
			y=point[1].split(",")[1][:-1]
			points[n]=(float(x),float(y))
			n+=1
	
		(x1,y1) = points[0]
		(x2,y2) = points[1]
		v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
#		print v, v_tr
	
		if v > v_tr:
			n_sacc+=1
			print "saccade: ",n_sacc,v
			fixated.value=0
			vel.append(v)

def detect_sacc_start(detector):
	detect.value=True
	detector[0].start() 

def detect_sacc_stop(detector):
	detector[0].terminate()
	#detect.value=False
	detector[0] = Process(target=detect_sacc, args=(v_tr,))


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

info = {'Velocity threshold':'0.5'}
infoDlg = gui.DlgFromDict(dictionary=info, title='WM experiment')
if infoDlg.OK:
    v_tr=float(info['Velocity threshold'])
if infoDlg.OK==False: core.quit() #user pressed cancel


record=Process(target=read_pupil,args=(finish,))
detector=[Process(target=detect_sacc, args=(v_tr,))]

info = {'Subject':'1'}
infoDlg = gui.DlgFromDict(dictionary=info, title='WM experiment')
if infoDlg.OK:
    outputname=info['Subject']
if infoDlg.OK==False: core.quit() #user pressed cancel



#create a window
mywin = visual.Window([800, 800],monitor="testMonitor", fullscr=False, units="cm") #create a window full screen
mouse=event.Mouse(win=mywin)
#mouse.setVisible(False)

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
    {'delay':float(delay), 'type':float(type), 'angle1':float(angle1),'ring1':float(ring1),'angle2':float(angle2),'ring2':float(ring2),'angle3':float(angle3),'ring3':float(ring3)}
    )   

stim_input.close()
#organise the trials 
trials = TrialHandler2(stimList,1,method='sequential')
trials.data.addDataType('choice')
trials.data.addDataType('fixated')
trials.data.addDataType('choiceAngle')
trials.data.addDataType('choiceR')
trials.data.addDataType('RT')# reaction time
trials.data.addDataType('MT')# movement time
trials.data.addDataType('ts_b')# timestamp begin trial
trials.data.addDataType('ts_f')# timestamp begin fixation
trials.data.addDataType('ts_p')# timestamp begin presentation
trials.data.addDataType('ts_d')# timestamp begin delay
trials.data.addDataType('ts_r')# timestamp begin response
trials.data.addDataType('ts_e')# timestamp end

#start the trials
trialClock = core.Clock()
totalClock = core.Clock()

totalClock.reset()
record.start()
for thisTrial in trials:
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

    detect_sacc_start(detector)

    while t<FIXATION:
        fixation.draw()
        mywin.flip()
        t=trialClock.getTime()    

  
    #draw the stimuli and update the window for the duration of stimulus presentation
    t=0
    trialClock.reset()
    ts_p = time()
    while t<PRESENTATION:
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
        if event.getKeys("escape"): exit_task()
        fixation.draw()
        mywin.flip()
        t=trialClock.getTime()

    detect_sacc_stop(detector)

   
    trials.data.add('fixated', fixated.value)
    
    if not fixated.value:
	#blacklist+=[hashlib.md5(str([trials.trialList[trials.thisIndex])).hexdigest()]]
	discarded +=[trials.trialList[trials.thisIndex]]
	continue

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
    
 
    trials.data.add('choice', list(choice_pos))
    trials.data.add('choiceAngle', choice_angle)
    trials.data.add('choiceR', choice_R)
    trials.data.add('RT', rtime)
    trials.data.add('MT', mtime)
    trials.data.add('ts_b',ts_b)# timestamp begin trial
    trials.data.add('ts_f',ts_f)# timestamp begin fixation
    trials.data.add('ts_p',ts_p)# timestamp begin presentation
    trials.data.add('ts_d',ts_d)# timestamp begin delay
    trials.data.add('ts_r',ts_r)
    trials.data.add('ts_e',ts_e)
    trials.saveAsText(fileName=outputname,   
		      dataOut=['choice_raw','choiceAngle_raw','choiceR_raw','RT_raw','MT_raw','ts_b','ts_f','ts_p','ts_d','ts_r','ts_e','fixated_raw'],
		      delim='\t', matrixOnly=False, appendFile=False)
    resp = visual.Circle(mywin,radius=0.3,pos=pos)
    resp.setFillColor('red')
    resp.draw()


trials.saveAsText(fileName=outputname,   
		  dataOut=['choice_raw','choiceAngle_raw','choiceR_raw','RT_raw','MT_raw','ts_b','ts_f','ts_p','ts_d','ts_r','ts_e','fixated_raw'],
		  delim='\t', matrixOnly=False, appendFile=False)


finish.value=1

record.join()


#f=open(outputname,'w')
#dump(trials,f)


stim1.clearTextures()
stim2.clearTextures()
stim3.clearTextures()
fixation.clearTextures()
mywin.flip()
trickwin = visual.Window([1280, 1024],monitor="testMonitor", fullscr=True, units="cm") #create a window full screen
thanksClock=core.Clock()
thanksText=visual.TextStim(win=trickwin, ori=0,
    text="""Thanks!""",
    pos=[0,0], height=1.5,
    rgb=[1, 1, 1])

continueThanks=True
t=0
thanksClock.reset()
while continueThanks and (t<2.0000):
    #get current time
    t=thanksClock.getTime()

    #update each component 
    if (1.0000 <= t < 2.0000):
        
        thanksText.draw()
      
    
    #check for quit (the [Esc] key)
    if event.getKeys("escape"): exit_task()
    event.clearEvents()#so that it doesn't get clogged with other events
    #refresh the screen
    trickwin.flip()

print totalClock.getTime()
#clean up
event.clearEvents()
trickwin.close()
mywin.close()
#core.quit()
    
