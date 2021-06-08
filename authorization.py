# imports
import pickle
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2 import service_account

def create_api(secrets_file, api_name, api_version, *scopes, cred_type = "service"):
    # constants
    secrets_file = secrets_file
    api_name = api_name
    api_version = api_version
    scopes = [scope for scope in scopes[0]]
    pickle_file = f"token_{api_name}_{api_version}.pickle"
    cred = None
    reset_cred = True

    # reset credentials
    if reset_cred and os.path.exists(pickle_file):
        os.remove(pickle_file)

    if cred_type == "client":
        if os.path.exists(pickle_file):
            # load file
            with open(pickle_file, "rb") as token:
                cred = pickle.load(token)

        # get credentials
        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(secrets_file, scopes)
                cred = flow.run_local_server()

            # write file
            with open(pickle_file, "wb") as token:
                pickle.dump(cred, token)

    elif cred_type == "service":
        cred = service_account.Credentials.from_service_account_file(secrets_file, scopes = scopes)
    
    else:
        print("invalid cred type:", cred_type)

    api = None
    try:
        api = build(api_name, api_version, credentials=cred)
        print(api_name + "_" + api_version + " created successfully.")
    except Exception as e:
        print("failed to create " + api_name + "_" + api_version)
        print("encountered error:")
        print("\t", e)
        os.remove(pickle_file)
    
    return api
