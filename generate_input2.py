#from psychopy import * #import all libraries from PsychoPy
import math
import numpy as np
from matplotlib.pyplot import plot,show,hist,subplots,tight_layout,savefig,ion
from matplotlib import rc
import pylab
from random import randrange,choice,shuffle

# TRIAL TYPES

CTRL=0
CW=1
CCW=2

IN=3
OUT=4

codes = ["CTRL","CW", "CCW", "IN","OUT"]
#rings
R1=8
R2=9
R3=10

Rs=[R1,R2,R3]

#delta of proximity
delta_t=[5,10,15]
delays = [[0],[3]]

ri=30
rf=60


CM=['Blue','Green', 'Grey', 'Orange', 'Purple', 'Red', 'Cyan']

def validate(trials):
    # atrials=np.array(trials)
    # T1 = map(cal_quadrant,a[:,3])
    # T2 = map(cal_quadrant,a[:,5])
    # T3 = map(cal_quadrant,a[:,7])

    return True

def calc_quadrant(angle):
  return int(angle) / 90 + 1

def oposite(quadrant):
    op=(quadrant+2)%4
    return (4 if op < 1 else op)

def genPos(quadrant):
    Q=(quadrant-1)*90
    angle=randrange(ri,rf,1)+Q
    return np.mod(angle,360)

def genCW(quadrant,R,delta):
    ring1=R
    probe=genPos(quadrant)
    neigh=probe-delta
    ring2=choice(Rs)
    return [ring1,probe,ring1,neigh]
    
def genCCW(quadrant,R,delta):
    ring1=R
    probe=genPos(quadrant)
    neigh=probe+delta
    ring2=choice(Rs)
    return [ring1,probe,ring1,neigh]
    
def genIO(quadrant,R_1,R_2):
    probe=genPos(quadrant)
    ring=choice(Rs)
    return [R_1,probe,R_2,probe]

def genIO2(quadrant):
    probe=genPos(quadrant)
    ring=choice([R1,R2])
    return [R2,probe,R1,probe]

def genRand(quadrant):
    Q=[q for q in [1,2,3,4] if q != quadrant]
    far1=genPos(quadrant)
    ring1=genR()

    q,Q=choicePop(Q)
    far2=genPos(q)
    ring2=genR()

    q,_=choicePop(Q)
    far3=genPos(q)
    ring3=genR()
    return [ring1,far1,ring2,far2]

def genR():
    r=randrange(Rs[0],Rs[2])
    r_d=randrange(1,9)/10.0
    return r+r_d

def choicePop(list):
    c=choice(list)
    i=0
    for n in list:
      if n == c: 
        new_list = list[0:i]+list[i+1:]
      i+=1
    return (c,new_list)

def genCtr(quadrant,R):
    ring1=R
    probe=genPos(quadrant)
    return [ring1,probe,-1,-1]

valid=False
trials=[]
while(not valid):
  valid = validate(trials)
  for d in delays:
    for q in range(1,4+1):

        # IN TRIALS
        trials.append(d+[IN]+genIO(q,Rs[0],Rs[1])) # dr1
        trials.append(d+[IN]+genIO(q,Rs[1],Rs[2])) # dr2
        trials.append(d+[IN]+genIO(q,Rs[0],Rs[2])) # dr3

        # OUT TRIALS
        trials.append(d+[OUT]+genIO(q,Rs[1],Rs[0])) # dr1
        trials.append(d+[OUT]+genIO(q,Rs[2],Rs[1])) # dr2
        trials.append(d+[OUT]+genIO(q,Rs[2],Rs[0])) # dr3
  
        # CW/CCW
        gens=[genCW,genCCW]*3
        types=[CW,CCW]*3
        idx = [0,1]*3

        # R1
        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[0],delta_t[0])) # R1 dt1

        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[0],delta_t[1])) # R1 dr2
      
        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[0],delta_t[2])) # R1 dr2

        # R3
        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[2],delta_t[0])) # R1 dt1

        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[2],delta_t[1])) # R1 dr2
      
        i,idx = choicePop(idx)
        trials.append(d+[types[i]]+gens[i](q,Rs[2],delta_t[2])) # R1 dr2

        # Controls
        trials.append(d+[CTRL]+genCtr(q,Rs[0]))
        trials.append(d+[CTRL]+genCtr(q,Rs[1]))
        trials.append(d+[CTRL]+genCtr(q,Rs[2]))

shuffle(trials)
shuffle(trials)

      

atrials=np.array(trials)

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 8}

rc('font', **font)


f,ax=subplots(3,2)
i=0
for j in [atrials[:,1]==k for k in [CTRL, CW, CCW, IN, OUT]]:
  axi = ax[i/2,np.mod(i,2)]
  points = list(atrials[j,3])+list(atrials[j,5])
  axi.hist(points,120,color=CM[i])
  axi.set_title(codes[i]+": "+str(len(points)))
  i+=1

ax[i/2,np.mod(i,2)].hist(list(atrials[:,3])+list(atrials[:,5]),100,color='k')
axi.set_title("All: "+str(len(points)))
tight_layout()
savefig('trials.png',dpi=500)

print "DELAY  TYPE  R1  T1  R2  T2  R3  T3"
while len(trials):
    t=trials.pop()
    print '\t'.join(map(str, t))

 




 
