import argparse
import sys
from os import path, remove
from datetime import datetime, timedelta
from gettext import translation
from humanize import filesize
from pkg_resources import resource_filename
from psutil import swap_memory, process_iter
from signal import signal, SIGINT
from time import sleep
from swapping_ebuilds.__init__ import __version__, __versiondate__
from colorama import Fore, init

try:
    t=translation('swapping_ebuilds', resource_filename("swapping_ebuilds","locale"))
    _=t.gettext
except:
    _=str

def signal_handler(signal, frame):
    print(_("You pressed 'Ctrl+C', exiting..."))
    exit(1)

class PackageManager:
    def __init__(self):
        self.arr=[]
        self.read_file()

    def read_file(self):
        f=open("/var/lib/swapping_ebuilds.txt","r")
        reports=[]
        for line in f.readlines():
            rep=Report().init__from_line(line)
            if rep is not None:
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
            if  p.number_of_reports_with_positive_swapping()*args.interval>args.hl_analyze*60:
                print (Fore.RED + _("{} [{}] has {} reports with {} of swap variation average and {} of swap average. They took {}").format(p.datetime(), p.name(), int(p.length()), filesize.naturalsize(int(p.average_diff())), filesize.naturalsize(int(p.average_swap())), p.duration())+ Fore.RESET)
            else:
                print ( _("{} [{}] has {} reports with {} of swap variation average and {} of swap average. They took {}").format(p.datetime(), p.name(), int(p.length()), filesize.naturalsize(int(p.average_diff())), filesize.naturalsize(int(p.average_swap())), p.duration()))


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
        return sum/self.length()

    # Variation in abs value
    def average_diff(self):
        sum=0
        for r in self.arr:
            sum=sum+abs(r.diff)
        return sum/self.length()

    def length(self):
        return len(self.arr)
        
    def number_of_reports_with_positive_swapping(self):
        n=0
        for r in self.arr:
            if r.isPositiveSwapping():
                n=n+1
        return n

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
        return self.length()/self.duration().total_seconds()*60*60

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
        
    ## Returns if the num last reposrts are swapping
    def are_last_reports_positive_swapping(self, arr_position):
        for i in range(arr_position-args.hl_list+1,  arr_position+1):
            if self.arr[i].isPositiveSwapping()==False:
                return False
        return True
        
    ## Returns if the last reports are consecutive
    def are_last_reports_consecutive(self, arr_position):
        if (self.arr[arr_position].datetime-self.arr[arr_position-args.hl_list+1].datetime).total_seconds()<args.hl_list*(args.interval+1):
            return True
        return False

    def print(self):
        for i,  rep in enumerate(self.arr):
            if i>=args.hl_list-1 and self.are_last_reports_positive_swapping(i) and self.are_last_reports_consecutive(i):
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
        
    def isSwapping(self):
        if self.diff!=0:
            return True
        return False

    def isPositiveSwapping(self):
        if self.isSwapping() and self.diff>0:
            return True
        return False

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
    
    group=parser.add_argument_group(_("Parameters"))
    group.add_argument('--interval', help=_('Seconds between medition. Default is 10'), action='store', type=int, default=10, metavar="s")
    group.add_argument('--hl_analyze', help=_('Minutes of positive swapping required to highlight ebuilds with --analyze. Default is 15'), action='store', type=int, default=15, metavar="m")
    group.add_argument('--hl_list', help=_('Number of consecutive logs with positive swapping required to highlight ebuilds with --list. Default is 3'), action='store', type=int, default=3, metavar="s")

    group1=parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--analyze', help=_('Analyze log'), action='store_true', default=False)
    group1.add_argument('--get', help=_('Generate log'), action='store_true',default=False)
    group1.add_argument('--clean', help=_('Clean log'), action='store_true',default=False)
    group1.add_argument('--list', help=_('List log'), action='store_true',default=False)

    global args
    args=parser.parse_args()

    filename="/var/lib/swapping_ebuilds.txt"

    if args.hl_analyze<0:
        print (_("--hl_analyze must be positive"))
        sys.exit(1)
        
    if args.hl_list<1:
        print (_("--hl_list must be greater than 1"))
        sys.exit(1)

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

    if args.get:
        last_swap=swap_memory().used
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
        set=PackageManager()
        set.print()
        sys.exit(0)
