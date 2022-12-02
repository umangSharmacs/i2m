import numpy as np
from scipy.io import wavfile
from bisect import bisect

class note_manager:
    def __init__(self):
        # Map notes to frequencies
        octave=['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B']
        self.base_freq=440
        keys=np.array([x+str(y) for y in range(0,9) for x in octave])
        start = np.where(keys == 'A0')[0][0]
        end = np.where(keys == 'C8')[0][0]
        keys = keys[start:end+1]
        self.note_freqs = dict(zip(keys, [2**((n+1-49)/12)*self.base_freq for n in range(len(keys))]))
        self.note_freqs[''] = 0.0
        self.factor=[i/10 for i in np.logspace(1,0,5)]
        self.sample_rate=44100
        #
    def get_sine_wave(self,frequency, duration, sample_rate=44100, amplitude=4096):
        t = np.linspace(0, duration, int(sample_rate*duration)) # Time axis
        wave = amplitude*np.sin(2*np.pi*frequency*t)
        return wave
      
    def apply_overtones(self,frequency, duration, factor, sample_rate=44100, amplitude=4096):
        freq=[frequency*i for i in range(1,5)]
        frequencies = np.minimum(np.array([frequency*(x+1) for x in range(len(factor))]), sample_rate//2)
        amplitudes = np.array([amplitude*x for x in factor])
        
        fundamental = self.get_sine_wave(frequencies[0], duration, sample_rate, amplitudes[0])
        for i in range(1, len(factor)):
            overtone = self.get_sine_wave(frequencies[i], duration, sample_rate, amplitudes[i])
            fundamental += overtone
        return fundamental

    def get_adsr_weights(self,frequency, duration, length, decay, sustain_level, sample_rate=44100):
        
        intervals = int(duration*frequency)
        len_A = np.maximum(int(intervals*length[0]),1)
        len_D = np.maximum(int(intervals*length[1]),1)
        len_S = np.maximum(int(intervals*length[2]),1)
        len_R = np.maximum(int(intervals*length[3]),1)
        
        decay_A = decay[0]
        decay_D = decay[1]
        decay_S = decay[2]
        decay_R = decay[3]
        
        A = 1/np.array([(1-decay_A)**n for n in range(len_A)])
        A = A/np.nanmax(A)
        D = np.array([(1-decay_D)**n for n in range(len_D)])
        D = D*(1-sustain_level)+sustain_level
        S = np.array([(1-decay_S)**n for n in range(len_S)])
        S = S*sustain_level
        R = np.array([(1-decay_R)**n for n in range(len_R)])
        R = R*S[-1]
        
        weights = np.concatenate((A,D,S,R))
        smoothing = np.array([0.1*(1-0.1)**n for n in range(5)])
        smoothing = smoothing/np.nansum(smoothing)
        weights = np.convolve(weights, smoothing, mode='same')
        
        weights = np.repeat(weights, int(sample_rate*duration/len(weights)))
        tail = int(sample_rate*duration-weights.shape[0])
        if tail > 0:
            weights = np.concatenate((weights, weights[-1]-weights[-1]/tail*np.arange(tail)))
        return weights

    def get_note(self,frequency,duration=2.5):
        note = self.apply_overtones(frequency, duration, factor=self.factor)
        weights = self.get_adsr_weights(frequency, duration, length=[0.1, 0.35, 0.45, 0.1],
                                decay=[0.075,0.04,0.01,0.1], sustain_level=0.2)
        note=note*weights
        note = note*(4096/np.max(note))
        return note

    def get_frequency(self, freq):

        chords=np.asarray(list(self.note_freqs.values()))
        index = (np.abs(chords-freq)).argmin()
        return chords[index]


    def make_music(self,frequencies_dict):
        music=np.array([])
        for freq,time in frequencies_dict.items():
            freq=self.get_frequency(freq)
            note=self.get_note(freq,time)
            music=np.append(music,note)
        print("Music created....", end=" ")
        wavfile.write('music.wav', rate=self.sample_rate, data=music.astype(np.int16))
        print("File Written")
        return music

