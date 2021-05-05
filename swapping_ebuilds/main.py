import argparse
import sys
from os import path, remove
from datetime import datetime, timedelta, date
from gettext import translation
from humanize import filesize
from pkg_resources import resource_filename
from psutil import swap_memory, process_iter
from signal import signal, SIGINT
from time import sleep
from swapping_ebuilds.__init__ import __version__, __versiondate__
from colorama import Fore, init
from math import floor, ceil
from numpy import array, percentile

try:
    t=translation('swapping_ebuilds', resource_filename("swapping_ebuilds","locale"))
    _=t.gettext
except:
    _=str

def signal_handler(signal, frame):
    print(_("You pressed 'Ctrl+C', exiting..."))
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
            print (_("{} [{}] has {} reports with {} of swap variation average and {} of swap average. They took {}").format(p.datetime(), p.name(), int(p.num_reports()), filesize.naturalsize(int(p.average_diff())), filesize.naturalsize(int(p.average_swap())), p.duration()))

class ReportManager:
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

    # Variation in abs value
    def average_diff(self):
        sum=0
        for r in self.arr:
            sum=sum+abs(r.diff)
        return sum/self.num_reports()

    def num_reports(self):
        return len(self.arr)

    def duration(self):
        if len(self.arr)==1:
            return timedelta(seconds=args.interval)
        return self.arr[len(self.arr)-1].datetime-self.arr[0].datetime

    def datetime(self):
        """
           Returns datetime of the first Result
        """
        return self.arr[0].datetime


    def reports_per_hour(self):
        return self.num_reports()/self.duration().total_seconds()*60*60


    def print(self):
        print(f"{rep.datetime} {rep.name} {filesize.naturalsize(rep.swap)} {filesize.naturalsize(rep.diff)}")


    def list_of_swap(self):
        r=[]
        for o in self.arr:
            r.append(o.swap)
        return r

    def list_of_variations(self):
        r=[]
        for o in self.arr:
            r.append(o.diff)
        return r

    def print(self):
        limit_diff=int(percentile(array(self.list_of_variations()), args.percentile))
        limit_swap=int(percentile(array(self.list_of_swap()), args.percentile))
        print(f"Percentile {args.percentile}: Swap {filesize.naturalsize(limit_swap)}, Diff {filesize.naturalsize(limit_diff)}")
        for rep in self.arr:
            if abs(rep.diff)>abs(limit_diff) and rep.swap>limit_swap:
                print(Fore.RED + f"{rep.datetime} {rep.name} {filesize.naturalsize(rep.swap)} {filesize.naturalsize(rep.diff)}" + Fore.RESET)
            else:
                print(f"{rep.datetime} {rep.name} {filesize.naturalsize(rep.swap)} {filesize.naturalsize(rep.diff)}")

def ReportManager_from_file(filename):
    rm=ReportManager()
    if path.exists(filename):
        for line in open(filename, "r").readlines():
            rep=Report().init__from_line(line)
            if rep is not None:
                rm.arr.append(rep)
    else:
        print(_("There isn't log to list"))
    return rm


## Used for analyze to join by ebuild
class Package(ReportManager):
    def __init__(self):
        ReportManager.__init__(self)

    def name(self):
        return self.arr[0].name

class Report:
    def __init__(self):
        self.datetime=None
        self.name=None
        self.swap=0
        self.diff=0

    def init__from_line(self,line):
        try:
            line=line[:-1]
            if line.find("  ")!=-1:#Not good line
                return None
            str_datetime=line.split(" [")[0]
            self.datetime=datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f")
            self.name=line.split(" [")[1].split("] ")[0]
            listIntegers=line.split(" [")[1].split("] ")[1].split(" ")
            self.swap=int(listIntegers[0])
            self.diff=int(listIntegers[1])
            return self
        except:
            print(_(f"Problem parsing: {line}"))
            return None

    def __repr__(self):
        return f"{self.datetime} {self.name} {self.swap} {self.diff}"
####################################################################################################

def main():
    init()
    signal(SIGINT, signal_handler)

    description=_("This app logs swap information in /var/lib/swapping_ebuilds.txt compiling Gentoo packages. This allow you to change in package.env the number of processors used, to decrease swapping and improve ebuild time compilation")
    epilog=_("Developed by Mariano Muñoz 2017-{}").format(__versiondate__.year)
    parser=argparse.ArgumentParser(description=description,epilog=epilog)
    parser.add_argument('--version',action='version', version=__version__)
    parser.add_argument('--interval', help=_('Seconds between medition. Default is 10'), action='store', type=int, default=10, metavar="seconds")
    parser.add_argument('--percentile', help=_('Percentile for list. Default is 75'), action='store', type=int, default=75, metavar="percentile")

    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--analyze', help=_('Analyze log'), action='store_true', default=False)
    group1.add_argument('--get', help=_('Generate log'), action='store_true',default=False)
    group1.add_argument('--clean', help=_('Clean log'), action='store_true',default=False)
    group1.add_argument('--list', help=_('List log'), action='store_true',default=False)

    global args
    args=parser.parse_args()

    filename="/var/lib/swapping_ebuilds.txt"

    if args.clean:
        if path.exists(filename):
            remove(filename)
            print(_("Log cleaned"))
        else:
            print(_("Log already cleaned"))
        sys.exit(0)

    if args.list:
        rm=ReportManager_from_file(filename)
        rm.print()
        sys.exit(0)

    last_swap=swap_memory().used
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
            diff=used-last_swap

            if package=="":
                print (_(f"{datetime.now()} Ebuild hasn't been detected. Swap: {filesize.naturalsize(used)} (Variation: {filesize.naturalsize(diff)})"))
            else:
                if diff!=0:
                    f=open(filename,"a")
                    f.write(f"{datetime.now()} {package} {used} {diff}\n")
                    f.close()
                    print (f"{datetime.now()} {package}. Swap: {filesize.naturalsize(used)} (Variation: {filesize.naturalsize(diff)}) Logging...")
                else:
                    print (f"{datetime.now()} {package}. Swap: {filesize.naturalsize(used)} (Variation: {filesize.naturalsize(diff)})")
            last_swap=used
            sleep(args.interval)
        sys.exit(0)

    if args.analyze:
        if path.exists(filename)==False:
            print(_("No swapping detected"))
            sys.exit(0)
        set=SetPackages()
        set.print()
        sys.exit(0)
