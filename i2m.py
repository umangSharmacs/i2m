from notes import note_manager
from images import img_manager
import librosa
import numpy as np
from scipy.io import wavfile

img_manager=img_manager('web_first_images_release.png')
red=img_manager.get_frequencies('r',0.2)
green=img_manager.get_frequencies('g',0.2)
blue=img_manager.get_frequencies('b',0.2)

note_manager=note_manager()


red=note_manager.make_music(red)
green=note_manager.make_music(green)
blue=note_manager.make_music(blue)
print(red)
print(green)
print(blue)
_maxshape=max(red.shape,green.shape,blue.shape)
red.resize(_maxshape)
green.resize(_maxshape)
blue.resize(_maxshape)

print(red.shape,green.shape,blue.shape)
music=(1/3)*red + (1/3)*green + (1/3)*blue
wavfile.write('music_combined_notes_rounded.wav', rate=44100, data=music.astype(np.int16))
#note_manager.make_music()