import urllib
from os import sep
from os.path import expanduser
import sys
import threading # thread.start_new_thread ( function, args[, kwargs] )
from  Queue import Queue, Empty

from time import sleep,time
# import filecmp
from os.path import isfile#,exists
# from os import path,walk,makedirs,rmdir,sep,remove



class ThreadedDownload:
	def __init__(this, threads = 1, tempdir = "~temp"):
		#init
		this.mNumThreads = threads
		this.mTempDir = tempdir
		#monitoring
		this.download_count = 0
		this.total_count = 0
		this.thread_status = []
		#threading
		this.mToDownload = Queue() # url,path, filename
		this.mStatus = Queue()
		this.thread_ids = []
		this.mQuit = 0
		#displaying
		this.mLastPrint = time()*1000
		
		#begin
		# this.addURLs(initArray)
		this.threadMonitorID = threading.Thread(target=this.threaded_monitor, args=())
		this.threadMonitorID.start()
		this.launchThreads()

	#PUBLIC FUNCTIONS
	def addURLs(this, array):
		if isinstance(array,tuple):
			this.mToDownload.put(array)
			this.total_count+=len(array)
		elif isinstance(array,list):
			(this.mToDownload.put(i) for i in array)
			this.total_count+=len(array)

		else:
			print("Invalid Input")

	#PRIVATE FUNCTIONS
	def launchThreads(this):
		for tid in range(this.mNumThreads):
			t = singleThread(tid,this.mToDownload,this.mStatus)
			this.thread_ids.append(t)
	def threaded_monitor(this): 
		for i in range(this.mNumThreads):
			this.thread_status.append([0,0,0])
		while (not this.mQuit) or (not this.mStatus.empty()):
			try:
				this.display(500)
				thread_num,file_url,file_percent,complete = this.mStatus.get(True,0.5) #false = no wait
				this.thread_status[thread_num] = (thread_num,file_percent,file_url)
				this.download_count +=complete # 1 or 0
			except Empty:
				pass

	def join(this):
		for i in this.thread_ids:
			i.mQuit = True
		for i in this.thread_ids:
			i.mTID.join()
		this.mQuit=True
		this.threadMonitorID.join()
		this.display()
		print("")
		

	def getStatus(this):
		return this.thread_status

	def display(this,delay=0):
		currentTime = time()*1000
		if (currentTime - this.mLastPrint < delay):
			return
		this.mLastPrint = currentTime
		sys.stdout.flush()
		sys.stdout.write(("\rTOTAL:{0:>3}/{1}, ").format(this.download_count,this.total_count))
		for i in this.thread_status:
			sys.stdout.write(("{1:>3}%").format(i[0]+1,i[1]))
    	
  





class singleThread:
	def __init__(this,tid, inQueue, outQueue):
		this.mTnum = tid
		this.mInQ = inQueue
		this.mOutQ = outQueue
		this.mQuit = 0
		this.mTID = threading.Thread(target=this.threaded_dl, args=(tid,))
		this.mTID.start()
		# this.mReportDelay=20
		

	def threaded_dl(this,tid):
		while (not this.mQuit) or (not this.mInQ.empty()):
			try:
				(this.path, this.url) = this.mInQ.get(True,1) #false = no wait
				if not isfile(this.path): urllib.urlretrieve(this.url, this.path, reporthook=this.dlProgress)
				this.mOutQ.put((this.mTnum,this.url,100,1))
			except Empty:
				pass
			


	def dlProgress(this,count, blockSize, totalSize):
			percent = int(count*blockSize*100/totalSize)
			this.mOutQ.put((this.mTnum,this.url,percent,0))



def example_main():
	root_dir = expanduser("~")
	path = root_dir + sep + 'Desktop' +sep +'test.txt'
	url = (path,"https://bootstrap.pypa.io/get-pip.py")
	# arr = [('asd','dsf','tre'),('asd','dsf','tre'),('asd','dsf','tre')]
	d = ThreadedDownload(10,url)
	# sleep(3)
	d.getStatus()
	d.addURLs(url)
	for i in range(20):
		d.addURLs(url)
		# sleep(0.2)

	# print d.mToDownload
	d.join()

	del d


