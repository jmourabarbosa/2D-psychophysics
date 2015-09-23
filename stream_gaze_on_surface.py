"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging  
"""
import zmq
from time import sleep,time

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
 
while True:
#    sleep(1)
    msg = socket.recv()

    items = msg.split("\n") 
    msg_type = items.pop(0)
    if msg_type == 'Pupil':
	pupil+=[items]
    else:
	gaze+=[items]
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
