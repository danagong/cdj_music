import json
import csv
import spotipy
import pandas as pd
import matplotlib.pyplot as plt

from spotipy.oauth2 import SpotifyClientCredentials

client_id = '47ba54eeec38449ebca556beee1b6a01'
client_secret = '5413feecd775481ca6e10ac3e14eae34'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

data = []

with open('data_short.csv', newline='') as f:
    data_reader = csv.reader(f, delimiter=',')

    # list of tuples -> spotify data -> json
    # basic tuple: (school, major, year, gender, intl/dom, spotify_user, spotify_playlist)

    for row in data_reader:
        if (row[8] == "Yes"):
            # school formatting
            school = row[2]
            school = school[school.find('(') + 1:school.find(')')]
            
            major = row[3]
            year = row[4]
            gender = row[5]
            intl_dom = row[6]

            # url formatting
            sp_prof = row[9]

            if (sp_prof.find("?si=") != -1):
                sp_prof = sp_prof[:sp_prof.find("?si=")]

            if (sp_prof.find("user/") != -1):
                sp_prof = sp_prof[sp_prof.find("user/") + 5:]
            
            
            data.append((school, major, year, gender, intl_dom, sp_prof))

playlist_dict = {}

'''
for user in data:
    user_id = user[5]

    playlists = sp.user_playlists(user_id)
    playlist_dict[user_id] = []

    playlists = playlists["items"]

    for p in playlists:
        playlist_dict[user_id].append(p["uri"])

with open("user_playlists.json", "w") as f:
    json.dump(playlist_dict, f)
'''

'''

with open("user_playlists.json", "r") as f:
    playlist_dict = json.load(f)

# objective: go through all playlists, aggregate all the songs in a json object along with demographic data

aggrsong_dict = {}

for ud in data:
    user_id = ud[5]
    aggrsong_dict[user_id] = {}

for ud, up in zip(data, playlist_dict.keys()):
    user_id = ud[5]
    
    aggrsong_dict[user_id]["playlists"] = playlist_dict[up]

    aggrsong_dict[user_id]["songs"] = []

    print("----- USER!!!!!!!: " + user_id)

    for pl in playlist_dict[up]:
        songs = sp.playlist_tracks(pl) 

        print("----- PLAYLIST!!!!!!!: " + pl)

        # TASK: build an iterator for playlist >100 songs

        for song in songs["items"]:
            try:
                target_uri = song["track"]["uri"]
                if "local" not in target_uri:
                    song_info_builder = {}
                    song_info_builder["uri"] = target_uri
                    # print(sp.audio_features(target_uri))
                    aggrsong_dict[user_id]["songs"].append(song_info_builder)
            except TypeError:
                pass

with open("user_songs.json", "w") as f:
    json.dump(aggrsong_dict, f)

'''

dataset_raw = {}

with open("user_songs.json", "r") as f:
    dataset_raw = json.load(f)

for ud, up in zip(data, dataset_raw.keys()):
    dataset_raw[up]["college"] = ud[0]
    dataset_raw[up]["major"] = ud[1].split(", ")
    dataset_raw[up]["year"] = ud[2]
    dataset_raw[up]["gender"] = ud[3]
    dataset_raw[up]["status"] = ud[4]

    # print(len(dataset_raw[up]["songs"]))

    ''' algorithm:
    iterate through songs, adding them to a list (while n < len(dataset_raw[up]["songs]), uri added to running list)
    every 100 songs (save start index)
        > call audio_features(uri running list)
        > go back and fill in JSON with values
    last batch X songs
    '''

    n = 0
    loop = 0

    while (n < len(dataset_raw[up]["songs"])):
        while(loop < (int(len(dataset_raw[up]["songs"]) / 100))):
            uri_list = []
            # loop through, 100 songs at a time (0..99, 100..199)
            for i in range(loop*100, (loop*100)+100):
                uri_list.append(dataset_raw[up]["songs"][i]["uri"])
            
            # call audio features
            output = sp.audio_features(uri_list)
            
            for i in range(0, 100):
                dataset_raw[up]["songs"][n]["features"] = output[i]
                n = n+1

            loop = loop + 1
        uri_list = []
        for i in range(n, len(dataset_raw[up]["songs"])):
            uri_list.append(dataset_raw[up]["songs"][i]["uri"])

        print(len(uri_list))
        
        output = sp.audio_features(uri_list)

        for i in range(0, len(uri_list)):
            dataset_raw[up]["songs"][n]["features"] = output[i]
            n = n+1
    print("all done")
    
with open("dataset_new.json", "w") as f:
    json.dump(dataset_raw, f)


    

            


            
                



with open("dataset.json", "w") as f:
    json.dump(dataset_raw, f)


# Final steps:
    # >>> build iterator for playlists w/ >100 songs
    # >>> best way to get audio_features() while minimizing n requests

