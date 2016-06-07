import subprocess
import os
import select
import shlex

class Client:
    def __init__(self, client, config, debug):
        jabberite = os.path.join(config["np1sec_path"], "jabberite")
        self.debug = debug
        command = jabberite +" --account=" + client["account"]+ " --password=\""+ client["password"] + "\" --server=" +  client["server"] + " --room=" + client["room"]
        self.process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr= subprocess.PIPE, env={"LD_LIBRARY_PATH": os.path.join(config["np1sec_path"], ".libs") + ":" + config["ld_library_path"]})
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout
        self.stderr = self.process.stderr
        self.inbuf = ""
        self.outbuf = ""
        self.errbuf = ""

    def communicate(self):
        self.outbuf = ""
        self.errbuf = ""
        ready = select.select([self.stdout, self.stderr], [self.stdin], [])  
        for fd in ready[0]:
            if fd == self.stdout:
                self.outbuf = self.stdout.readline()
                if self.debug:
                    print self.outbuf,
            if fd == self.stderr:
                self.errbuf = self.stderr.readline()
                if self.debug:
                    print self.errbuf,
        for fd in ready[1]:
            if fd == self.stdin:
                if self.inbuf:
                    self.stdin.write(self.inbuf)
