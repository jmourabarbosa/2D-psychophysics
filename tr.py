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
from multiprocessing import Process, Value,Array,Queue
from time import sleep,time
import matplotlib.pyplot as plt

p_dir = "subjects"

# TIMES
FIXATION=1
PRESENTATION=1

colors=['green','blue','white']


#Pupil network setup
port = "5000"
localhost="tcp://127.0.0.1:"
genis="tcp://10.201.99.188:"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(localhost+port)
socket.setsockopt(zmq.SUBSCRIBE, '')

finish = Value('i',0)
detect = Value('i',1)

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
	print "vou tentar"
	msg = socket.recv()
        items = msg.split("\n")
        msg_type = items.pop(0)

	while msg_type != "Gaze":
		print "trying"
		msg = socket.recv()
	        items = msg.split("\n")
        	msg_type = items.pop(0)
	return items

def get_vel(vels):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect(localhost+port)
	socket.setsockopt(zmq.SUBSCRIBE, 'Gaze')

	while detect.value:
		n = 0
		times=[0,0]
		points = [0,0]
		while n<2:
			msg = socket.recv()
		        items = msg.split("\n")
			items.pop(0)
			times[n]=float(items[-2].split(":")[1])
			point = items[0].split(":")
			x=point[1].split(",")[0][1:]
			y=point[1].split(",")[1][:-1]
			points[n]=(float(x),float(y))
			n+=1
	
		(x1,y1) = points[0]
		(x2,y2) = points[1]
		v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
		#print v	
		vels.put(v)


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

vels = Queue()
record=Process(target=read_pupil,args=(finish,))
detector=Process(target=get_vel,args=(vels,))

'' 
