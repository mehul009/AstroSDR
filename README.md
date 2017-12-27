# frequency_detector_rtlsdr
Radio frequency detector software for RtlSdr,written in python for astronomical use and also common use in collage project 
for run this software you need pyrtlsdr, pyqt5, matplotlib, pickutils installed on your system if not than please install in via pip or conda 

for run this simple right    python3 Detector.py     in terminal


It is simple GUI software containing one input tab and slider for change the central frequency 
and it also contain zoom facility , you can active this facility from the View menu and for use this , go into the Help-->Zoom
Changing SampleRate and also OverLapping is availble in Edit menu

i also add a save option in file menu for the save shown figure and peak value in .png file ,simply click screen shot  in file menu and your image is save in the directory where you run this coad(name of file is 'psd of central frequency <central _freq> .png' )

New feature for save incoming raw data in HDF5 formate are add for , for active this feature go in file menu and active a save data chekbox and see in your home/astronomy directory for saved data

for more information and bug and also for extra features suggetion email me on below address
mehulsutariya09@gmail.com

