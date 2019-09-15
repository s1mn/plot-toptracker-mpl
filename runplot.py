#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 2019

import csv
import dateutil.parser
import datetime
import matplotlib.pyplot
import random

filename  = "toptracker_2020_01_02_03_04.csv"
startproj = dateutil.parser.parse('2019-06-01T12:00:00+00:00') # software project start date
endproj   = dateutil.parser.parse('2019-12-31T12:00:00+00:00') # software project end date
starttime = dateutil.parser.parse('2019-06-01T12:00:00+00:00') # plot start date
endtime   = dateutil.parser.parse('2019-11-30T12:00:00+00:00') # plot end date
timeperperson = 1000 # hours each person is supposed to work over [startproj,endproj]
teamsize = 10
figureprops = {"font.family": "Linux Libertine O"}
figuresize = (7,2)

timeallpeople = timeperperson * teamsize
entries = []
authorsset = set()

class Entry:
    def __init__(self, dict):
        self.author = dict['workers']
        authorsset.add(self.author)
        self.duration = int(dict['duration_seconds'])
        self.time = dateutil.parser.parse(dict['start_time'])

class DateSlot:
    def __init__(self, date, authors, prev):
        self.date = date
        self.times = {}
        self.aggrtimes = {}
        for author in authors:
            self.times[author] = self.aggrtimes[author] = 0
        if prev:
            for author in authors:
                self.aggrtimes[author] += prev.aggrtimes[author]

    def add(self, author, duration):
        self.times[author] += duration
        self.aggrtimes[author] += duration
    
    @property
    def total(self):
        return sum(self.times.values())

    @property
    def aggrtotal(self):
        return sum(self.aggrtimes.values())

with open(filename, 'r') as timecsv:
    reader = csv.reader(timecsv)
    head = next(reader)
    for row in reader:
        entries.append(Entry(dict(zip(head,row))))

authors = list(authorsset)
authors.sort()
authors_random = authors.copy()
random.shuffle(authors_random) # anonymize

dateslots, futureslots = [], []
granularity = datetime.timedelta(days=1)

slot = None
curtime = starttime
while curtime < endtime:
    nexttime = curtime + granularity
    slot = DateSlot(curtime, authors, slot)
    for entry in entries:
        if entry.time >= curtime and entry.time < nexttime:
            slot.add(entry.author, entry.duration)
    dateslots.append(slot)
    curtime = nexttime

while curtime <= endproj:
    nexttime = curtime + granularity
    slot = DateSlot(curtime, [], None)
    futureslots.append(slot)
    curtime = nexttime

matplotlib.pyplot.rcParams.update(figureprops)

matplotlib.pyplot.figure(figsize=figuresize)
matplotlib.pyplot.plot_date(
        x=[s.date for s in dateslots], xdate=True,
        y=[s.aggrtotal/3600 for s in dateslots],
        fmt='-')
matplotlib.pyplot.plot_date(
        x=[s.date for s in dateslots + futureslots], xdate=True,
        y=[0 if s.date < startproj else
           (s.date-startproj)/(endproj-startproj)*timeallpeople
           for s in dateslots + futureslots],
        fmt='-k')
matplotlib.pyplot.savefig("timelogged-total.pdf", bbox_inches='tight', pad_inches=0)
matplotlib.pyplot.show()

matplotlib.pyplot.figure(figsize=figuresize)
for author in authors_random:
    matplotlib.pyplot.plot_date(
            x=[s.date for s in dateslots], xdate=True,
            y=[s.aggrtimes[author]/3600 for s in dateslots], fmt='-')
matplotlib.pyplot.plot_date(
        x=[s.date for s in dateslots + futureslots], xdate=True,
        y=[0 if s.date < startproj else
           (s.date-startproj)/(endproj-startproj)*timeperperson
           for s in dateslots + futureslots],
        fmt='-k')
matplotlib.pyplot.savefig("timelogged-individual.pdf", bbox_inches='tight', pad_inches=0)
matplotlib.pyplot.show()
