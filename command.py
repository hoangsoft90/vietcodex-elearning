import subprocess, threading
import sys
import os
import signal

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def log(self,str):
        f=open("log.txt","w")          #create new file
        f.truncate()
        f.write(str)
        f.close()

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.f = open(r'log.txt','w')
            self.process = subprocess.Popen(self.cmd, shell=True,stdout=self.f, stderr=subprocess.PIPE)
            self.output, self.err  = self.process.communicate()
            self.f.close()
            """
            out = self.process.stdout.read(1)

            i=0
            while True:
                out = self.process.stdout.read(1)
                if out == '' and self.process.poll() != None:
                    break
                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()
                i+=1
            """
            print 'Thread finished=> %s' %self.output
            #self.log( self.output)

        thread = threading.Thread(target=target,args=[])
        thread.start()


        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            self.process.kill()
            os.kill(self.process.pid, signal.SIGTERM)

            print "command.py",os.fstat(self.f.fileno()).st_size
            #thread.join()  #continue thread , please do not because i need to exit app
        print self.process.returncode