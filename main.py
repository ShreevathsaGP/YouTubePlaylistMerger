# imports
import os
import json
import re
from googleapiclient.discovery import build
import authorization as custom_auth
import time

# create api instance
client_secret_file = "client_secrets.json"
service_secret_file = "service_secrets.json"
api_name = "youtube"
api_version = "v3"
scopes = ["https://www.googleapis.com/auth/youtube"]
youtube = custom_auth.create_service(client_secret_file, api_name, api_version, scopes, cred_type = "client")

# playlists to merge
merge_playlists = [
        ]
target_playlist = ""
next_page_token = "first"
extra = 0

# api loop
while next_page_token != None:
    # iterate over merge_playlists
    for playlist_id in merge_playlists:
        print("Playlist ID: {}".format(playlist_id))
        # make playlist get request
        if next_page_token == "first":
            playlist_request = youtube.playlistItems().list(
                    part = "contentDetails",
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = None
                    )
        else:
            playlist_request = youtube.playlistItems().list(
                    part = "contentDetails",
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token
                    )

        # get videos in playlist
        playlist_response = playlist_request.execute()
        videos = [item["contentDetails"]["videoId"] for item in playlist_response["items"]]
        video_request = youtube.videos().list(
                part = "snippet",
                id = ",".join(videos)
                )
        video_response = video_request.execute()
        videos = video_response["items"]

        # add video to target
        for video in videos:
            title = video["snippet"]["title"]
            video_id = video["id"]
            add_video_request = youtube.playlistItems().insert(
                    part = "snippet",
                    body = {
                        "snippet": {
                            "playlistId": target_playlist,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                                }
                            }
                        }
                    )
            add_video_response = add_video_request.execute()
        
        # check page
        next_page_token = playlist_response.get("nextPageToken")
