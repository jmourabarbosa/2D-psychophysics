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
from pupil_support import *


data=open(sys.argv[1],'r')
data = np.array(data) 

idx = where(data=='')

i=0

for j in idx:
	item = data[i:j]
	new_data+=[item]
	i=j+1



