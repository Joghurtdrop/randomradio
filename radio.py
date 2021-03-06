import subprocess
import random
import time
import re
import httplib2
import tkinter

class Radio():
    def __init__(self):
        self.channel='Noch nichts gehoert'
        self.history = [['Ich bin Ihr erster Sender :D','und ich der erste Link :p']]

    def getstream(self):
        h = httplib2.Http(".cache")
        # Genres holen
        resp, page = h.request('http://www.radio.de', 'GET')
        genrePat = re.compile(b'href=\"\/genre\/.*\/\"')
        genreUrls = [i.decode('utf-8') for i in re.findall(genrePat,page)]
        genreUrls = ['http://www.radio.de' + i[6:-1] for i in genreUrls]
        genre = random.choice(genreUrls)
        genre = genre.replace(' ','%20')
        print(genre)
        resp, page = h.request(genre, 'GET')
        # Nutz nur die erste Seite des Genres
        sitePat = re.compile(b'<li><a href="\?.*">')
        sites = [i.decode('utf-8') for i in re.findall(sitePat,page)]
        sites = [genre+'?p=1']+[genre + i[13:-2] for i in sites]
        localsite = random.choice(sites)
        resp, page = h.request(localsite, 'GET')
        channelPat = re.compile(b'\/\/[^.]*.radio.de\" class=\"stationinfo-link\"')
        channels = [i.decode('utf-8') for i in re.findall(channelPat, page)]
        channels = ['http:' + i[:-26] for i in channels]
        # Die Radioseite öffnen und Stream holen
        self.channel=random.choice(channels)
        resp, page = h.request(self.channel, 'GET')
        streamPat = re.compile(b'\"streamUrl\":\"[^\"]*\"')
        self.stream = [i.decode('utf-8') for i in re.findall(streamPat, page)][0][13:-1]
        print(self.stream)

    def start(self):
        print('start')
        self.getstream()
        self.add_history()
        self.mplayer = subprocess.Popen('mplayer ' + self.stream +' -novideo -ao alsa -quiet -slave', stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE , shell=True)

    def stop(self):
        print('stop')
        try:
            self.mplayer.terminate()
            self.mplayer.wait()
        except:
            pass

    def print_channel(self):
        print(self.history)

    def add_history(self):
        if len(self.history)>=8:
            self.del_last_history()
        self.history.append([self.channel,self.stream])

    def del_last_history(self):
        self.history.pop(0)



radio = Radio()

top = tkinter.Tk()
top.wm_title('RandomRadio')

def timeclock():
    if (state):
        global timer
        timer[2] +=1

        if (timer[2] >= 60):
            timer[2] = 0
            timer[1]+= 1

        if(timer[1] >= 60):
            timer[1] = 0
            timer[0]+= 1
        
        if timerstate:
            if(timer[1] >= 15):
                bforward()

        timestring = pattern.format(timer[0],timer[1],timer[2])
        timelabel.configure(text=timestring)
    top.after(1000,timeclock)

def bstop():
    start.configure(state='normal')
    stop.configure(state='disable')
    radio.stop()
    stoptimer()

def bstart():
    start.configure(state='disable')
    stop.configure(state='normal')
    starttimer()
    radio.start()
    main_var.set(radio.channel)

def bforward():
    start.configure(state='disable')
    stop.configure(state='normal')
    starttimer()
    radio.stop()
    time.sleep(1)
    radio.start()
    time.sleep(1)
    global mutestate
    if mutestate:
        mutestate = False
        bmute()
    main_var.set(radio.channel)

def stoptimer():
    global state
    state = False

def starttimer():
    global state
    state = True
    global timer
    timer = [0,0,0]
    timelabel.configure(text='00:00:00')

def bmute():
    radio.mplayer.stdin.write(b'mute\n')
    global mutestate
    if mutestate:
        mutebutton.configure(relief='raised')
        mutestate = False
    else:
        mutebutton.configure(relief='sunken')
        mutestate = True

def history_window():
    global window
    try:
        window.destroy()
    except:
        pass
    window = tkinter.Toplevel(top)
    history_string=""
    for s in radio.history:
        history_string+=s[0]+'\n'+s[1]+'\n'+'\n'
    history_string = history_string[:-2]
    history_var.set(history_string)
    history_label = tkinter.Label(window,textvariable=history_var).pack()

def quitit():
    radio.stop()
    top.quit()

def bnexttimer():
    global timerstate
    if timerstate:
        nexttimer.configure(relief='raised')
        forward.configure(state='normal')
        timerstate = False
    else:
        nexttimer.configure(relief='sunken')
        forward.configure(state='disable')
        timerstate = True


main_var=tkinter.StringVar()
label = tkinter.Label(top,textvariable=main_var)
label.pack()

window = tkinter.Toplevel(top)
window.destroy()

history_var=tkinter.StringVar()

state = False
timer = [0,0,0]
pattern = '{0:02d}:{1:02d}:{2:02d}'
timelabel=tkinter.Label(text='00:00:00')
timelabel.pack()


mutestate = False
mutebutton = tkinter.Button(top,text='Mute',command=bmute)
mutebutton.pack()

timerstate= True
nexttimer = tkinter.Button(top,text='15min Timer',command=bnexttimer,relief='sunken')
nexttimer.pack()

forward = tkinter.Button(top,text='Forward',state='disable',command=bforward)
forward.pack()

start = tkinter.Button(top,text='Starte',command=bstart)
start.pack()

history = tkinter.Button(top,text='History',command=history_window)
history.pack()

stop = tkinter.Button(top,text='Stoppe',command=bstop)
stop.pack()

quit = tkinter.Button(top,text='Quit',command=quitit)
quit.pack()

timeclock()
top.mainloop()

#while True:
#    mplayer=startradio()
#    time.sleep(10)
#    stopradio(mplayer)
