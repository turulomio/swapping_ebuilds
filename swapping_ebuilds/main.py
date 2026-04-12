import argparse
import sys
from os import path, remove
from datetime import datetime, timedelta
from gettext import translation
from humanize import filesize
from importlib.resources import files
from psutil import swap_memory, process_iter
from signal import signal, SIGINT
from time import sleep
from swapping_ebuilds.__init__ import __version__, __versiondate__
from colorama import Fore, init

# Initialize gettext for internationalization.
# If translation files are not found, it falls back to using the original strings.
try:
    t=translation('swapping_ebuilds', files("swapping_ebuilds") / "locale")
    _=t.gettext
except:
    _=str

def signal_handler(signal_received, frame):
    """
    Handles the SIGINT signal (Ctrl+C) to gracefully exit the script.
    """
    print(_("You pressed 'Ctrl+C', exiting..."))
    exit(1)

class PackageManager:
    """
    Manages a collection of Package objects, grouping individual swap reports
    by the ebuild they belong to. This class is primarily used for the
    `--analyze` functionality.
    """
    def __init__(self):
        self.arr=[]
        self.read_file()

    def read_file(self):
        """
        Reads the log file (`/var/lib/swapping_ebuilds.txt`) and populates
        the `arr` attribute with `Package` objects. Each `Package` object
        contains a series of `Report` objects for a specific ebuild.
        """
        f=open("/var/lib/swapping_ebuilds.txt","r")
        reports=[]
        # Read all reports from the file
        for line in f.readlines():
            rep=Report().init__from_line(line)
            if rep is not None:
                reports.append(rep)

        if len(reports)==0:
            return

        last_report=reports[0]
        package=Package() # Initialize the first package
        
        # Group reports by package name
        for r in reports:
            if last_report.name==r.name:
                 package.arr.append(r)
            else:
                 # When a new package is encountered, save the current package
                 # and start a new one.
                 self.arr.append(package)
                 package=Package()
                 package.arr.append(r)
            last_report=r
        self.arr.append(package)
        
    def print(self):
        """
        Prints the analysis report for each package.
        Highlights packages that meet the `--hl_analyze` criteria in red.
        If `--hl_only` is true, only highlighted packages are shown.
        """
        for p in self.arr:
            if  p.number_of_reports_with_swapping()*args.interval>args.hl_analyze*60:
                print (Fore.RED + _("{} [{}] has {} reports with {} of swap variation average and {} of swap average. They took {}").format(p.datetime(), p.name(), int(p.length()), filesize.naturalsize(int(p.average_diff())), filesize.naturalsize(int(p.average_swap())), p.duration())+ Fore.RESET)
            else:
                if args.hl_only==False:
                    print ( _("{} [{}] has {} reports with {} of swap variation average and {} of swap average. They took {}").format(p.datetime(), p.name(), int(p.length()), filesize.naturalsize(int(p.average_diff())), filesize.naturalsize(int(p.average_swap())), p.duration()))


class ReportManager:
    """
    A base class for managing a collection of `Report` objects.
    Provides methods for calculating averages, durations, and filtering reports.
    Both `PackageManager` (indirectly via `Package`) and the `--list` command
    use this class.
    """
    def __init__(self):
        self.arr: list[Report] = []

    def average_swap(self):
        sum=0
        for r in self.arr:
            sum=sum+r.swap
        return sum/self.length()

    # Variation in abs value
    def average_diff(self):
        """
        Calculates the average absolute variation in swap usage across all reports.
        """
        sum=0
        for r in self.arr:
            sum=sum+abs(r.diff)
        return sum/self.length()

    def length(self):
        """
        Returns the number of reports in the manager.
        """
        return len(self.arr)
        
    def number_of_reports_with_swapping(self):
        n=0
        for r in self.arr:
            if r.isSwapping():
                n=n+1
        return n

    def duration(self):
        """
        Calculates the total duration covered by the reports.
        """
        if len(self.arr)==1:
            return timedelta(seconds=args.interval)
        return self.arr[len(self.arr)-1].datetime-self.arr[0].datetime

    def datetime(self):
        """
        Returns the datetime of the first report in the collection.
        This is used as the start time for a package's compilation or a log entry.
        """
        return self.arr[0].datetime

    def reports_per_hour(self):
        return self.length()/self.duration().total_seconds()*60*60

    def list_of_swap(self):
        """
        Returns a list of swap usage values from all reports.
        """
        r=[]
        for o in self.arr:
            r.append(o.swap)
        return r

    def list_of_variations(self):
        r=[]
        """
        Returns a list of swap variation values from all reports.
        """
        for o in self.arr:
            r.append(o.diff)
        return r
        
    def are_last_reports_swapping(self, arr_position):
        """
        Checks if the last `args.hl_list` reports, ending at `arr_position`,
        all indicate swapping (i.e., `diff != 0`).
        """
        for i in range(arr_position-args.hl_list+1,  arr_position+1):
            if self.arr[i].isSwapping()==False:
                return False
        return True
        
    def are_last_reports_consecutive(self, arr_position):
        """
        Checks if the last `args.hl_list` reports, ending at `arr_position`,
        are consecutive in time, allowing for a small margin of `args.interval`.
        This helps to filter out sporadic swap events.
        """
        if (self.arr[arr_position].datetime-self.arr[arr_position-args.hl_list+1].datetime).total_seconds()<args.hl_list*(args.interval+1):
            return True
        return False

    def print(self):
        """
        Prints each individual report.
        Highlights a sequence of reports in red if they meet the
        `--hl_list` and consecutiveness criteria.
        If `--hl_only` is true, only highlighted records are shown.
        This method is used by the `--list` command.
        """
        for i,  rep in enumerate(self.arr):
            if i>=args.hl_list-1 and self.are_last_reports_swapping(i) and self.are_last_reports_consecutive(i):
                print(Fore.RED + f"{rep.datetime} {rep.name} {filesize.naturalsize(rep.swap)} {filesize.naturalsize(rep.diff)}" + Fore.RESET)
            else:
                if args.hl_only==False:
                    print(f"{rep.datetime} {rep.name} {filesize.naturalsize(rep.swap)} {filesize.naturalsize(rep.diff)}")

def ReportManager_from_file(filename):
    """
    Creates a `ReportManager` instance by reading all `Report` objects
    from the specified log file.
    """
    rm=ReportManager()
    if path.exists(filename):
        for line in open(filename, "r").readlines():
            rep=Report().init__from_line(line)
            if rep is not None:
                rm.arr.append(rep)
    else:
        print(_("There isn't log to list"))
    return rm

class Package(ReportManager):
    """
    Represents a single ebuild package and its associated swap reports.
    It inherits from `ReportManager` to leverage its methods for
    calculating averages and durations for a specific package.
    Used internally by `PackageManager` for analysis.
    """
    def __init__(self):
        ReportManager.__init__(self)

    def name(self):
        """
        Returns the name of the ebuild package.
        Assumes all reports in this package belong to the same ebuild.
        """
        return self.arr[0].name

class Report:
    """
    Represents a single swap measurement event for an ebuild.
    Stores datetime, ebuild name, total swap used, and the change in swap.
    """
    def __init__(self):
        self.datetime: datetime | None = None
        self.name=None
        self.swap=0
        self.diff=0

    def isSwapping(self):
        if self.diff!=0:
            return True
        return False

    def init__from_line(self,line):
        """
        Initializes a Report object from a single line of the log file.
        The expected format is: "YYYY-MM-DD HH:MM:SS.ffffff [ebuild_name] swap_used swap_diff"
        
        Args:
            line (str): A string representing a log entry.
        Returns:
            Report or None: The initialized Report object if successful, None otherwise.
        """
        try:
            line=line[:-1]
            # Parse datetime, ebuild name, swap used, and swap difference
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
    
    group=parser.add_argument_group(_("Optional Parameters"))
    group.add_argument('--interval', help=_('Seconds between measurements. Default is 10'), action='store', type=int, default=10, metavar="s")
    group.add_argument('--hl_analyze', help=_('Minutes of swapping required to highlight ebuilds with --analyze. Default is 15'), action='store', type=int, default=15, metavar="m")
    group.add_argument('--hl_list', help=_('Number of consecutive logs with swapping required to highlight with --list. Default is 3'), action='store', type=int, default=3, metavar="s")
    group.add_argument('--hl_only', help=_('Shows in --list and --analyze only highlighted records'), action='store_true', default=False)

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
        # Clean the log file
        print(_("Attempting to clean log file..."))
        if path.exists(filename):
            remove(filename)
            print(_("Log cleaned"))
        else:
            print(_("Log already cleaned"))
        sys.exit(0)

    if args.list:
        # List raw log entries
        print(_("Listing log entries:"))
        rm=ReportManager_from_file(filename)
        rm.print()
        sys.exit(0)

    if args.get:
        # Generate log by continuously monitoring swap and ebuilds
        last_swap=swap_memory().used
        print(_(f"Monitoring swap usage every {args.interval} seconds. Press Ctrl+C to stop."))
        while True:
            package=""
            try:
                for proc in process_iter():
                    for word in proc.cmdline():
                        if word.endswith("] sandbox"):
                            package=word.replace(" sandbox","")
            except Exception:
                # Handle cases where process_iter might fail or a process disappears
                pass
            
            used=swap_memory().used
            diff=used-last_swap

            if package=="":
                print (_(f"{datetime.now()} Ebuild hasn't been detected. Swap: {filesize.naturalsize(used)} (Variation: {filesize.naturalsize(diff)})"))
            else:
                # Only log if there's a change in swap usage.
                # This avoids cluttering the log with entries where no swapping
                # occurred for an active ebuild.
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
        # Analyze the log file and print a summary report
        if path.exists(filename)==False:
            print(_("No swapping detected"))
            sys.exit(0)
        set=PackageManager()
        set.print()
        sys.exit(0)
