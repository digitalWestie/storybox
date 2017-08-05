#!/usr/bin/python

import csv
from sys import argv
import wave
from ID3 import *
import time

#song = ID3("voicemail.m4a")
#print song

playlists = { 'all': [] }
storage_path = '/home/digitalwestie/Code/storybox/'
recordings_path = storage_path + 'recordings/'
csv_path =  recordings_path + 'recordings.csv'

def writePlaylist(playlist, filepaths):
  print "Writing playlist " + playlist
  target = open(playlist+".m3u", 'w')
  target.truncate()
  target.write("#EXTM3U")
  for path in filepaths:
    song = ID3(path)
    target.write("\n")
    trackline = "#EXTINF:" + str(getDuration(path)) + "," + song["TITLE"] + " - " + song["ARTIST"]
    target.write(trackline.strip())
    target.write("\n")
    target.write(path)
    target.write("\n")
  target.close()

def getDuration(path):
  f = wave.open(path,'r')
  frames = f.getnframes()
  rate = f.getframerate()
  return int(frames / float(rate))

def tagRecording(recording):
  song = ID3(recordings_path+recording[0]+'.wav')
  song["ARTIST"] = recording[1]
  song["TITLE"] = recording[5] + ": " + recording[2]
  #song["DATE"] = recording[5] # not settable with ID3 
  song["GENRE"] = 37
  return True

def buildPlaylists(recording):
  categories = recording[4].split(';')
  for category in categories:
    category = category.strip()
    playlists.setdefault(category,[]).append(recordings_path+recording[0]+'.wav')
  era = recording[3]
  playlists.setdefault(era,[]).append(recordings_path+recording[0]+'.wav')
  playlists['all'].append(recordings_path+recording[0]+'.wav')

# ============================ #

reader = csv.reader(open(csv_path, 'r'))
recordings = list(reader)
del recordings[0]

for recording in recordings:
  if len(recording[1]) == 0:
    continue
  tagRecording(recording)
  buildPlaylists(recording)

for playlist, filepaths in playlists.items():
  writePlaylist(playlist, filepaths)
