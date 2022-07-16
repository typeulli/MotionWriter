from os import system
from os.path import dirname, realpath, exists
from time import localtime, strftime, time

folder = dirname(realpath(__file__)) + "\\"
file_path = folder+"logs\\" + strftime('%Y-%m-%d', localtime(time()))
n = 0
while exists(file_path+"-"+str(n)+".log"): n += 1
file_path += "-"+str(n)+".log"
#open(file_path, "w").close()
print(file_path)
system("python "+folder+"MotionWriter.py >> "+file_path)