# AstroSDR
Radio frequency detector software for RtlSdr. 
It is written in python for astronomical use which is commonly use in short or college term projects. 
To run this software we need pyrtlsdr, pyqt5, matplotlib, pickutils installed in our system ,if not then please install via pip or conda.

To run this simply write,  'python3 Detector.py  '  in terminal 


It is a simple GUI software containing one input tab and slider for changing the central frequency. 
It's having zoom facility which you can look up in the View menu and to use this, go into the Help-->Zoom
Changing the SampleRate and also OverLapping is availble in Edit menu.

Thers's a save option in file menu to the save shown figure and peak value in .png file ,simply click screen shot in file menu and your image will get saved in the current directory (name of file will be as 'psd of central frequency <central _freq> .png' )

To save incoming raw data in HDF5 format. go in file menu and click on save data chekbox and see in your present working  directory'/astronomy directory for saved data.

To change the the logo as per your need for your application ,just rename your desire image  as 'logo.png' (Working for linux, didn't checked for windows and mac OS) and put that image in same directory as where you opened your Detector software.

for more information, extra features and bug related issues, drop a message to following mail address
mehulsutariya09@gmail.com
Any suggeston is more than welcome!

