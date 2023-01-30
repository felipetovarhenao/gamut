from gamut.mosaic import Mosaic

# -------------------------------
# WRITE AN GAMuT MOSAIC TO DISK AS AUDIO
# -------------------------------

# 1) read previously created mosaic
mosaic = Mosaic()
mosaic.read('/path/to/my_mosaic.gamut')

# 2) convert to audio and write to disk as .wav
audio = mosaic.to_audio()
audio.write('/path/to/audio.wav')
