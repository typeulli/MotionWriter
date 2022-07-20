from os import system
from os.path import dirname, realpath, exists
from time import localtime, strftime, time

folder = dirname(realpath(__file__)) + "\\"
file_path = folder+"logs\\" + strftime('%Y-%m-%d', localtime(time()))
n = 0
while {True:exists(file_path+".log"), False:exists(file_path+"-"+str(n)+".log")}[n==0]: n += 1
if n > 0: file_path += "-"+str(n)
file_path += ".log"
#open(file_path, "w").close()
system("python "+folder+"MotionWriter.py --onHandler >> "+file_path)