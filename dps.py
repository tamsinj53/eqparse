import time
import os
import sys
import re
import datetime
import glob
import curses


def follow(thefile):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line

def latest_file(folder_path):
    file_type = r'/eqlog*.txt'
    files = glob.glob(folder_path + file_type)
    return max(files, key=os.path.getctime)


class player:
    def __init__(self,name):
          self.name=name
          self.dmg_out=0
          self.dmg_in=0
          self.now=datetime.datetime.now()
          self.hits=[]
          self.dps=0
        
    def hit(self,target,amount,time_string):
        try:
            amount=int(amount)
        except:
             print(f"{amount=}")
             raise
        self.dmg_out+=amount
        # [Mon Mar 27 16:09:32 2023]
        time_stamp = datetime.datetime.strptime(time_string,'%a %b %d %H:%M:%S %Y')
        self.now=time_stamp
        self.hits+=[(amount,time_stamp)]
        self.accounting()
        # print(f"{self.name} - {self.dps:.2f} dps {len(self.hits)} hits/min")

    def accounting(self):
        window=self.now-datetime.timedelta(seconds=60)
        self.hits=[hit for hit in self.hits if hit[1]>window]
        total=sum([hit[0] for hit in self.hits])
        self.dps=total/60.0

    def hit_by(self,agressor,amount):
        self.dmg_in+=amount

def display(stdscr,players):
    width=curses.COLS
    for i in players:
        pass
    stdscr.refresh()

def main(stdscr):
    while True:
        logfile_name=latest_file("/mnt/h/Games/Everquest/Logs")
        print(logfile_name)
        players={ "You": player("You") }

        logfile = open(logfile_name)
        loglines = follow(logfile)
        # iterate over the generator
        for line in loglines:
            latest_logfile=latest_file("/mnt/h/Games/Everquest/Logs")
            if latest_logfile != logfile_name:
                break
            line=line.strip()
            # print(line)
            match = re.match("\[(.*)\] ([^ ]+) (backstab|punch|bash|strike|crush|pierce|kick|hit|slash) (.+) for ([0-9]+) points of damage",line)
            if not match:
                match = re.match("\[(.*)\] ([^ ]+) (backstabs|punches|strikes|bashes|crushes|pierces|kicks|hits|slashes) (.+) for ([0-9]+) points of damage",line)
            if not match:
                match = re.match("\[(.*)\] ([^ ]+) (Scores a critical) (hit!)\(([0-9]+)\)",line)
            if not match:
                match = re.match("\[(.*)\] ([^ ]+) (Lands a Crippling) (Blow!)\(([0-9]+)\)",line)
            # if not match:
            #     match = re.match("\[(.*)\] (.+) (for ([0-9]+) points of damage",line)
            #     print(f"Unmatched: {line}")

            # [Wed Apr 05 20:25:11 2023] Fallalot crushes a ghoul for 18 points of damage.  
            # [Wed Apr 05 20:34:01 2023] a barbed bone skeleton was hit by non-melee for 1 points of damage.      
                
            if match:
                try:
                    time_string=match.group(1)
                    source=match.group(2)
                    dmg_type=match.group(3)
                    target=match.group(4)
                    amount=match.group(5)
                except:
                     print(line)
                     print(match.group(1))
                     print(match.group(2))
                     print(match.group(3))
                     print(match.group(4))
                     raise
                if source not in players:
                    players[source]=player(source)
                players[source].hit(time_string=time_string,target=target,amount=amount)
            display(stdscr,players)

if __name__ == '__main__':
    curses.wrapper(main)
