#from psychopy import * #import all libraries from PsychoPy
import math
import numpy as np
from matplotlib.pyplot import plot,show,hist,subplots,tight_layout,savefig,ion
from matplotlib import rc
import pylab
from random import randrange,choice,shuffle

# TRIAL TYPES
FARIO=0
FARCW=1
RAN=2

CCW=3
CW=4

IN=5
OUT=6
codes = ["FARIO", "FARCW", "RAN", "CCW", "CW", "IN","OUT"]
#rings
R1=8
R2=9
R3=10

Rs=[R1,R2,R3]

#delta of proximity
delta_t=[5,10,20]
delay = [[0],[3]]


CM=['Blue','Green', 'Grey', 'Orange', 'Purple', 'Red', 'Cyan']

def validate(trials):
    atrials=np.array(trials)
    T1 = map(cal_quadrant,a[:,3])
    T2 = map(cal_quadrant,a[:,5])
    T3 = map(cal_quadrant,a[:,7])

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
    far=genPos(oposite(quadrant))
    return [ring1,probe,ring1,neigh,ring2,far]
    
def genCCW(quadrant,R,delta):
    ring1=R
    probe=genPos(quadrant)
    neigh=probe+delta
    ring2=choice(Rs)
    far=genPos(oposite(quadrant))
    return [ring1,probe,ring1,neigh,ring2,far]
    
def genIO(quadrant,R_1,R_2):
    probe=genPos(quadrant)
    ring=choice(Rs)
    far=genPos(oposite(quadrant))
    return [R_1,probe,R_2,probe,ring,far]

def genIO2(quadrant):
    probe=genPos(quadrant)
    ring=choice([R1,R2])
    far=genPos(oposite(quadrant))
    return [R2,probe,R1,probe,ring,far]

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
    return [ring1,far1,ring2,far2,ring3,far3]

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

valid=False
while(not valid):

  trials = []

  # tighten extremes
  ri=30
  rf=60

  # In R1
  Q=range(1,4+1)
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[IN]+genIO(q,Rs[0],Rs[1])) # dr1
  trials.append(delay[1]+[IN]+genIO(q,Rs[0],Rs[1])) # dr1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[IN]+genIO(q,Rs[0],Rs[2])) # dr2
  trials.append(delay[1]+[IN]+genIO(q,Rs[0],Rs[2])) # dr2


  # Out R3
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[OUT]+genIO(q,Rs[2],Rs[1])) # dr1
  trials.append(delay[1]+[OUT]+genIO(q,Rs[2],Rs[1])) # dr1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[OUT]+genIO(q,Rs[2],Rs[0])) #  dr2
  trials.append(delay[1]+[OUT]+genIO(q,Rs[2],Rs[0])) #  dr2

  Q=range(1,4+1)
  # In / Out R2
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[OUT]+genIO(q,Rs[1],Rs[0])) # Out dr1
  trials.append(delay[1]+[OUT]+genIO(q,Rs[1],Rs[0])) # Out dr1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[IN]+genIO(q,Rs[1],Rs[2])) # In dr1
  trials.append(delay[1]+[IN]+genIO(q,Rs[1],Rs[2])) # In dr1

  # two random extra
  (q,Q) = choicePop(Q)
  r1,rs=choicePop([0,1,2])
  r2,rs=choicePop(rs)
  t=(IN if r1 < r2 else OUT)
  trials.append(delay[0]+[t]+genIO(q,Rs[r1],Rs[r2]))
  trials.append(delay[1]+[t]+genIO(q,Rs[r1],Rs[r2]))
  r1,rs=choicePop([0,1,2])
  r2,rs=choicePop(rs)

  if t == IN and r1 < r2: r1,r2=r2,r1
  if t == OUT and r1 > r2: r1,r2=r2,r1
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[IN if r1 < r2 else OUT]+genIO(q,Rs[r1],Rs[r2]))
  trials.append(delay[1]+[IN if r1 < r2 else OUT]+genIO(q,Rs[r1],Rs[r2]))


  # CW
  Q=range(1,4+1)
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CW]+genCW(q,Rs[0],delta_t[0])) # R1 dt1
  trials.append(delay[1]+[CW]+genCW(q,Rs[0],delta_t[0])) # R1 dt1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CW]+genCW(q,Rs[0],delta_t[1])) # R1 dr2
  trials.append(delay[1]+[CW]+genCW(q,Rs[0],delta_t[1])) # R1 dr2

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CW]+genCW(q,Rs[2],delta_t[0])) # R3 dt1
  trials.append(delay[1]+[CW]+genCW(q,Rs[2],delta_t[0])) # R3 dt1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CW]+genCW(q,Rs[2],delta_t[1])) # R3 dr2
  trials.append(delay[1]+[CW]+genCW(q,Rs[2],delta_t[1])) # R3 dr2

  # CCW
  Q=range(1,4+1)
  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CCW]+genCCW(q,Rs[0],delta_t[0])) # R1 dt1
  trials.append(delay[1]+[CCW]+genCCW(q,Rs[0],delta_t[0])) # R1 dt1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CCW]+genCCW(q,Rs[0],delta_t[1])) # R1 dr2
  trials.append(delay[1]+[CCW]+genCCW(q,Rs[0],delta_t[1])) # R1 dr2

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CCW]+genCCW(q,Rs[2],delta_t[0])) # R3 dt1
  trials.append(delay[1]+[CCW]+genCCW(q,Rs[2],delta_t[0])) # R3 dt1

  (q,Q) = choicePop(Q)
  trials.append(delay[0]+[CCW]+genCCW(q,Rs[2],delta_t[1])) # R3 dr2
  trials.append(delay[1]+[CCW]+genCCW(q,Rs[2],delta_t[1])) # R3 dr2

  for i in [0,1]:
    # open extremes
    ri=0
    rf=90

    # FAR CW
    Q=range(1,4+1)
    (q,Q) = choicePop(Q)
    far=genCCW(q,Rs[0],delta_t[0]) 
    trials.append(delay[i]+[FARCW]+[far[j] for j in [4,5,0,1,2,3]]) # R1 CW dt1
    (q,Q) = choicePop(Q)
    far=genCW(q,Rs[2],delta_t[0]) 
    trials.append(delay[i]+[FARCW]+[far[j] for j in [4,5,0,1,2,3]]) # R3 CW dt1
    (q,Q) = choicePop(Q)
    far=genCCW(q,Rs[0],delta_t[1])
    trials.append(delay[i]+[FARCW]+[far[j] for j in [4,5,0,1,2,3]]) # R1 CW dt2
    (q,Q) = choicePop(Q)
    far=genCW(q,Rs[2],delta_t[1])
    trials.append(delay[i]+[FARCW]+[far[j] for j in [4,5,0,1,2,3]]) # R2 CW d2

    # FAR IO
    Q=range(1,4+1)
    (q,Q) = choicePop(Q)
    far=genIO(q,Rs[0],Rs[1]) # In R1 dr1
    trials.append(delay[i]+[FARIO]+[far[j] for j in [4,5,0,1,2,3]])
    (q,Q) = choicePop(Q)
    far=genIO(q,Rs[0],Rs[2]) # In R1 dr1
    trials.append(delay[i]+[FARIO]+[far[j] for j in [4,5,0,1,2,3]])
    (q,Q) = choicePop(Q)
    far=genIO(q,Rs[1],Rs[2]) # In R1 dr1
    trials.append(delay[i]+[FARIO]+[far[j] for j in [4,5,0,1,2,3]])
    r1,rs=choicePop(range(1,3))
    r2,_=choicePop(rs)
    far=genIO(q,Rs[r1],Rs[r2]) # In R1 dr1
    trials.append(delay[i]+[FARIO]+[far[j] for j in [4,5,0,1,2,3]])


    # Random
    Q=range(1,4+1)*3 # 24 Random, 12 por delay
    for q in Q: 
       trials.append(delay[i]+[RAN]+genRand(q))
       valid=validate(trials)


shuffle(trials)
shuffle(trials)

atrials=np.array(trials)

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 8}

rc('font', **font)


f,ax=subplots(3,3)
i=0
for j in [atrials[:,1]==k for k in [FARIO, FARCW, RAN, CCW, CW, IN, OUT]]:
	axi = ax[i/3,np.mod(i,3)]
	points = list(atrials[j,3])+list(atrials[j,5])+list(atrials[j,7])
	axi.hist(points,120,color=CM[i])
	axi.set_title(codes[i]+": "+str(len(points)))
	i+=1

ax[i/3,np.mod(i,3)].hist(list(atrials[:,3])+list(atrials[:,5])+list(atrials[:,7]),100,color='k')
axi.set_title("All: "+str(len(points)))
tight_layout()
savefig('trials.png',dpi=500)

print "DELAY	TYPE	R1	T1	R2	T2	R3	T3"
while len(trials):
    t=trials.pop()
    print '\t'.join(map(str, t))

 
