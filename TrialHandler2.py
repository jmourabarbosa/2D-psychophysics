import os
from pickle import dump
import numpy as np
from random import randrange


class TrialHandler2(object):

    def __init__(self,trial_list=[],data_dict=[],subject_name='subject_name',pdir='subjects'):
        self.data_dict = {}
        self.trial_list = trial_list
        self.inext_trial = 0
        self.n_trials = len(trial_list)
        self.subject = subject_name
        self.dir = pdir
        n=0
        while os.path.exists(pdir+"/"+self.subject): 
            n+=1
        self.log_path=self.dir+"/"+self.subject+"_"+str(n)
    
    def add_type(self,key):
        self.data_dict[key]=[]
    
    def add_data(self,key,data):
        self.data_dict[key].append(data)

    def empty(self):
        b=self.n_trials<self.inext_trial+1
        if b: print "empty!"
        return b

    def next_trial(self):

        trial = self.trial_list[self.inext_trial]
        self.inext_trial+=1
        return trial

    # Assumies logging of repetition reason is done inside the main loop
    def repeat_trial(self,trial):

        for key in self.data_dict.keys():
            if len(self.data_dict[key]) < self.inext_trial:
               self.add_data(key,np.nan) 

        if self.empty():
            return False

        self.n_trials+=1
        # There is just on more trial, apend at the end
        if self.inext_trial == self.n_trials - 1: 
            self.trial_list.append(trial)
            return True

        # Generate random position, except the next trial
        new_pos = randrange(self.inext_trial+1,self.n_trials)
        self.trial_list.insert(new_pos,trial)
        return True

    def save_log(self, only_matrix=False, append=False, file=None):

        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

        # How data will appear: tab delim and 2 decimals
        form_stims = "\t\t".join(['%.2f']*len(self.trial_list[0]) )
        form_data = "\t\t".join(['%.2f']*len(self.data_dict))

        header = "\t\t".join(self.trial_list[0].keys() + self.data_dict.keys())
        
        body_stims = [form_stims % tuple(t.values()) for t in self.trial_list]
        
        data = np.array(self.data_dict.values())
        body_data  = [form_data % tuple(data[:,n]) for n in range(self.n_trials)]

        body = "\n".join([body_stims[t] + "\t\t" + body_data[t] for t in range(self.n_trials)])

        fid = open(self.log_path+'.pickle','w')
        dump(self,fid)
        fid.close()

        fid = open(self.log_path+'.txt','w')
        fid.write(header)
        fid.write(body)
        fid.close()

        print header
        print body