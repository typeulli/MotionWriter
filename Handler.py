from subprocess import call
from os.path import dirname, realpath, exists
from time import localtime, strftime, time
from sys import argv

folder = dirname(realpath(__file__)) + "\\"
file_path = folder+"logs\\" + strftime('%Y-%m-%d', localtime(time()))
n = 0
while {True:exists(file_path+".log"), False:exists(file_path+"-"+str(n)+".log")}[n==0]: n += 1
if n > 0: file_path += "-"+str(n)
file_path += ".log"
#open(file_path, "w").close()
try: call(folder+"MotionWriter.exe " + " ".join(argv[1:]) + " --onHandler >> "+file_path)
except: pass
try: call("python "+folder+"MotionWriter.py " + " ".join(argv[1:]) + " --onHandler >> "+file_path)
except: pass