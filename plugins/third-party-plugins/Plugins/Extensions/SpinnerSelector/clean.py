import os

for i in range(64):
	if (os.path.isfile("/usr/share/enigma2/wait%d.png"%(i+1))):
		os.system("rm -f /usr/share/enigma2/wait%d.png"%(i+1))
