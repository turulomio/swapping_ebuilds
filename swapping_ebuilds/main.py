#!/usr/bin/python3
import argparse
import sys
from os import path
from datetime import datetime, timedelta, date
from gettext import translation
from humanize import filesize
from pkg_resources import resource_filename
from psutil import swap_memory, process_iter
from signal import signal, SIGINT
from time import sleep
from swapping_ebuilds.__init__ import __version__, __versiondate__

try:
    t=translation('swapping_ebuilds', resource_filename("swapping_ebuilds","locale"))
    _=t.gettext
except:
    _=str



def signal_handler(signal, frame):
    print("You pressed 'Ctrl+C', exiting...")
    exit(1)



class SetPackages:
    def __init__(self):
        self.arr=[]
        self.read_file()

    def read_file(self):
        f=open("/var/lib/swapping_ebuilds.txt","r")
        last=None
        reports=[]
        for line in f.readlines():
            rep=Report().init__from_line(line)
            if rep!=None:
                reports.append(rep)

        if len(reports)==0:
            return

        last_report=reports[0]
        package=Package()
        for r in reports:
            if last_report.name==r.name:
                 package.arr.append(r)
            else:
                 self.arr.append(package)
                 package=Package()
                 package.arr.append(r)
            last_report=r
        self.arr.append(package)

    def print(self):
        for p in self.arr:
            print (_("{} ({}) [{}] has {} reports ({} per hour) with {} of swap average").format(p.datetime(), p.duration(),p.name(),p.num_reports(), int(p.reports_per_hour()),filesize.naturalsize(int(p.average_swap()))))


class Package:
    """
       Group of Reports
    """
    def __init__(self):
        self.arr=[]

    def average_swap(self):
        sum=0
        for r in self.arr:
            sum=sum+r.swap
        return sum/self.num_reports()

    def num_reports(self):
        return len(self.arr)

    def duration(self):
        if len(self.arr)==1:
            return timedelta(seconds=60)
        return self.arr[len(self.arr)-1].datetime-self.arr[0].datetime

    def datetime(self):
        """
           Returns datetime of the first Result
        """
        return self.arr[0].datetime
    def name(self):
        return self.arr[0].name
    def reports_per_hour(self):
        return self.num_reports()/self.duration().total_seconds()*60*60

class Report:
    def __init__(self):
        self.datetime=None
        self.name=None
        self.swap=0

    def init__from_line(self,line):
        try:
            line=line[:-1]
            if line.find("  ")!=-1:#Not good line
                return None
            str_datetime=line.split(" [")[0]
            self.datetime=datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f")
            self.name=line.split(" [")[1].split("] ")[0]
            self.swap=int(line.split(" [")[1].split("] ")[1])
            return self
        except:
            print(_(f"Problem parsing: {line}"))
            return None

    def __repr__(self):
        return "{} {} {}".format(self.datetime,self.name,self.swap)
####################################################################################################


def main():
    signal(SIGINT, signal_handler)

    description=_("This app logs in /var/lib/swapping_ebuilds.txt when compiling gentoo packages and swap is over an amount of MB. This allow you to change in package.env the number of processors used, to decrease swapping and improve ebuild time compilation")
    epilog=_("Developed by Mariano Muñoz 2017-{}").format(__versiondate__.year)
    parser=argparse.ArgumentParser(description=description,epilog=epilog)
    parser.add_argument('--version',action='version', version=__version__)
    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--analyze', help=_('Analyze log'), action='store_true', default=False)
    group1.add_argument('--get', help=_('Generate log'), action='store_true',default=False)
    parser.add_argument('--megabytes', help=_('Minimum megabytes swap amount to be logged. Default is 500MB'), action='store', default=500,metavar="MB")
    args=parser.parse_args()

    try:
        args.megabytes=int(args.megabytes)
    except:
        print(_("Please add a int to the megabytes argument"))
        sys.exit(0)

    filename="/var/lib/swapping_ebuilds.txt"

    if args.get:
        while True:
            package=""
            try:
                for proc in process_iter():
                    for word in proc.cmdline():
                        if word.endswith("] sandbox"):
                            package=word.replace(" sandbox","")
            except:
                pass

            used=swap_memory().used
            if used>args.megabytes*1024*1024:
                f=open(filename,"a")
                f.write(f"{datetime.now()} {package} {used}\n")
                f.close()
                print (f"{datetime.now()} {package} {filesize.naturalsize(used)} Logging...")
            else:
                print (f"{datetime.now()} {package} {filesize.naturalsize(used)}")
            sleep(60)

    if args.analyze:
        if path.exists(filename)==False:
            print(_("No swapping detected"))
            sys.exit(0)
        set=SetPackages()
        set.print()