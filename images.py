from PIL import Image
import numpy as np
from collections import OrderedDict

class img_manager:
    def __init__(self, img_path) -> None:
        self.im = Image.open(img_path).convert('RGB')
        #self.r, self.g, self.b = im.split()

    def get_rgb(self,threshold_limit=0.5):
        na = np.array(self.im).astype(np.float)
        self.red=na[...,0]
        self.red=self.red.flatten()
        r_max=self.red.max()
        threshold=threshold_limit*r_max
        total_len=len(self.red)
        self.red=[i if i>=threshold else 0 for i in self.red]

        self.green=na[...,1]
        self.green=self.green.flatten()
        g_max=self.green.max()
        threshold=threshold_limit*g_max
        total_len=len(self.green)
        self.green=[i if i>=threshold else 0 for i in self.green]

        self.blue=na[...,2]
        self.blue=self.blue.flatten()
        b_max=self.blue.max()
        threshold=threshold_limit*b_max
        total_len=len(self.blue)
        self.blue=[i if i>=threshold else 0 for i in self.blue]

        return self.red, self.green, self.blue

    def get_frequencies(self,channel, threshold_limit):
        self.get_rgb(threshold_limit)
        if channel=='r':
            temp=self.red
        elif channel=='g':
            temp=self.green
        elif channel=='b':
            temp=self.blue
        d=OrderedDict()
        prev=0
        s=0
        for i in temp:
            if i==0:
                s+=1
            else:
                d[prev]=s
                prev=i
                s=0
        d=list(d.items())
        freq=OrderedDict()
        index=0
        n=len(d)
        while True and index<n:
            k,v=d[index]
            if v!=0:
                freq[k]=v
                index+=1
                continue
            else:
                i=index
                temp=[]
                k_temp,v_temp=k,v
                while v_temp==0 and i<n:
                    temp.append(d[i])
                    v_temp=d[i][1]
                    i+=1
                #temp.append(d[i+1])
                index=i+2
                k_avg=sum([k for k,v in temp])/len(temp)
                v=temp[-1][1]
                freq[k_avg]=v
                continue

        freq=list(freq.items())
        frequencies=[k for k,v in freq]
        times=[v for k,v in freq]
        
        max_times=max(times)
        min_times=min(times)
        maximum_time_threshold=10
        times=[((i-min_times)*maximum_time_threshold)/(max_times-min_times) for i in times]

        note_min=27.5
        note_max=2186.009044809578
        max_freq=max(frequencies)
        min_freq=min(frequencies)
        frequencies=[((i-min_freq)/(max_freq-min_freq))*(note_max-note_min)+note_min for i in frequencies]

        music=OrderedDict()
        for f,t in zip(frequencies,times):
            if t!=0:
                music[f-1000]=round(t,2)

        return music