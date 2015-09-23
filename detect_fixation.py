"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging  
"""
import matplotlib.pyplot as plt
import zmq
from time import sleep,time
import numpy as np

#network setup
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, '')
surface_name = 'spread'
pupil=[]
gaze=[]
vel=[]
xx=[]
yy=[]
timess=[]
n_sacc=0
while True:
	n = 0
	times=[0,0]
	points = [0,0]
	while n<2:
		print "antes"
		msg = socket.recv()

		items = msg.split("\n") 
		msg_type = items.pop(0)
		if msg_type == 'Gaze':
			#print items
			times[n]=float(items[-2].split(":")[1])
			timess.append(times[n])
			point = items[0].split(":")
			x=point[1].split(",")[0][1:]
			y=point[1].split(",")[1][:-1]
			xx.append(x)
			yy.append(y)
			points[n]=(float(x),float(y))
			
			n+=1

	(x1,y1) = points[0]
	(x2,y2) = points[1]
	v = np.sqrt((x2-x1)**2 + (y2-y1)**2)/(times[1]-times[0])
	#print v
	if v>0.5:
		n_sacc+=1
		print n_sacc,"saccade!"
	vel.append(v)
    	#items3 = items[3].split("\n")
   	#print time(),float(items[2].split(":")[-3].split(" ")[1][:-1])
'''
msg = socket.recv()

items = msg.split("\n") 
msg_type = items.pop(0)
#if msg_type == 'Gaze':
#items3 = items[3].split("\n")
	
  	#print time(),float(items[2].split(":")[-3].split(" ")[1][:-1])
print time(),items[-3:]
'''
