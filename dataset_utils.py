from __future__ import unicode_literals

import glob
import os
import random
import librosa
import numpy as np
import tensorflow as tf
import xml.etree.ElementTree as ET
import csv
import time
import youtube_dl
import logging

from pydub import AudioSegment
from datetime import datetime 


def normalize_wav(wav_dir, sampling_rate, audio_ext):

    file_list = glob.glob(os.path.join(wav_dir, audio_ext))
    
    # Iterate over the channels audio files
    for fn in file_list:

        # Load the audio time series and its sampling rate
        sound_clip,s = librosa.load(fn, sr=sampling_rate) #sample input files at 16kHz

        file_name = os.path.basename(fn)
        dest_path = os.path.join(wav_dir,'normalized',file_name)
        librosa.output.write_wav(dest_path, y=sound_clip, sr=sampling_rate, norm=True)

# Transform categorical labels by enumerating one boolean column for each category
# indicator vector for each class label

def one_hot_encode(labels):
    """builds the hot encoded labels  in case of many nominal class labels
    :param labels: the nominal labels
    :type numpy vector of int values (dimension=1)
    :returns: A matrix of the one-hot encoded `labels`
    :raises: -
    """
    n_labels = len(labels)
    n_unique_labels = len(np.unique(labels))
    #prepare the matrix with rows= size of the dataset and columns= number of distinct labels
    one_hot_encode = np.zeros((n_labels,n_unique_labels))
    #add `1` in the corresponding label column for each row 
    one_hot_encode[np.arange(n_labels), labels] = 1
    
    print("Labels size [AFTER one-hot encode]: ",one_hot_encode.shape)
    
    return one_hot_encode


# Forrmat training set for the LibLinear library usage 

def liblinear_data_format(features, labels):
    data=[]

    for i,vector in enumerate(features):
        row=[]

        # Append the label
        if int(labels[i])==1:
            row.append('+1')
        else:
            row.append('-1')

        # Append the values as <index>:<value>
        for j,value in enumerate(vector):
            index=j+1
            row.append(str(index)+':'+str(value))

        # Return the feature vector
        data.append(row)

    return data


def TRStoCSV(parent_dir, sub_dirs):
    """Transform a TRS file to a CSV file
    :param trsfile: path to TRS file
    :raises: -
    """


    file_ext = "*.trs"
    utter_list = []
    
    #sub_dirs = ['S01','S02','S03','S04','S05','S06','S07','S08','S09','S10',
    #            'S11','S12','S13','S14','S15','S16','S17','S18','S19','S20',
    #            'S21']
    
    for sub_dir in sub_dirs:
        for fn in glob.glob(os.path.join(parent_dir, sub_dir, file_ext)):
            
            utter_list = []
            tree = ET.parse(fn)
            root = tree.getroot()
            
            # open a file for writing
            csv_name = os.path.basename(fn).split('.')[0]
            csv_data = open(parent_dir+'/CSV/'+csv_name+'.csv', 'w')
        
            # create the csv writer object
            csvwriter = csv.writer(csv_data)
            
            csv_head = []
            csv_head.append('start')
            csv_head.append('end')
            csv_head.append('utterance')
            
            csvwriter.writerow(csv_head)
            
            turn = -99
            start_times=[]
        
            for i,sync in enumerate(root.findall(".//Sync")):
                
                #if it corresponds to the `start` sync tag
                if (sync.tail.replace('\n', '') and
                    (sync.attrib['time'] not in start_times) and
                    (i != turn+1)):
                    turn = i
                    utter = []*3
                    utter.insert(0, sync.attrib['time'])
                    start_times.append(sync.attrib['time'])
                    sync_tail = sync.tail.replace('\n', '')
                    utter.insert(2, sync_tail)
                    
                else:
                    #if it corresponds to the `end` sync tag
                    if i == turn+1:
                        utter.insert(1, sync.attrib['time'])
                        utter_list.append(utter)
                        print(utter)
                        csvwriter.writerow(utter)

                        # if it's an end and a start tag at the same time
                        if sync.tail.replace('\n', ''):
                            turn = i
                            utter = []*3
                            utter.insert(0, sync.attrib['time'])
                            sync_tail = sync.tail.replace('\n', '')
                            utter.insert(2, sync_tail)


                    #othrwise
                    else:
                        continue


        
            csv_data.close()
    

def download_youtube_audio(yid, start, end, label):
    
        ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        }
        
        youtube_url_base = 'https://youtu.be'
    
        if label is not None:
            ydl_opts["outtmpl"]= audioset_dir+'/Audio/yvid__%(id)s__'+str(label)+'.%(ext)s'
        
        # Join URL elements as in `youtu.be/m55Fx5rDh8g?start=50&end=60`
        youtube_url = youtube_url_base + '/' + yid + '?start=' + str(start) + '&end=' + str(end)
    
        r = None
    
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            r = ydl.extract_info(youtube_url, download=False)

    
        audiofile = AudioSegment.from_wav(audioset_dir+'/Audio/yvid__'+r['id']+'__'+str(label)+'.wav')
        sliced = audiofile[int(float(row[1])*1000):int(float(row[2])*1000)]
        sliced.export(audioset_dir+'/Audio/yvid__'+r['id']+'__'+str(label)+'.wav', format="wav")
    
    else:
        print(yid+': Already exists!')


if __name__ == "__main__":
    #logger = configure_logging()
main()
