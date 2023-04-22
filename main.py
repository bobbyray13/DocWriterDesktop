import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace the following values with your own credentials and the desired folder ID
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
SERVICE_ACCOUNT_FILE = 'location of service account file here.json'
FOLDER_ID = 'last string of google drive folder URL here'

# Authenticate using service account credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Use the Google Drive API to get a list of files in the specified folder
drive_service = build('drive', 'v3', credentials=creds)
results = drive_service.files().list(q=f"'{FOLDER_ID}' in parents and trashed = false",
                                     fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

# Print the names of all files in the specified folder
if not items:
    print('No files found.')
else:
    print('Files in the specified folder:')
    for item in items:
        print(f"{item['name']} ({item['id']})")

# Prompt user to choose an action
while True:
    action = input("What would you like to do? (NewDocument, EditDocument, Quit): ")
    if action == "NewDocument":
        # Prompt user for file name
        file_name = input("Please enter a name for your new document: ")
        # Create a new Google Docs document in the specified folder
        doc_metadata = {'name': file_name, 'parents': [FOLDER_ID], 'mimeType': 'application/vnd.google-apps.document'}
        doc = drive_service.files().create(body=doc_metadata).execute()
        # Use the Google Docs API to get the document ID
        doc_id = doc['id']
        # Print confirmation message to user
        print(f"{file_name} has been created in the specified folder.")
    elif action == "EditDocument":
        # Prompt user for file name and add text to the document
        doc_name = input("Please enter the name of the document you would like to edit: ")
        doc_id = None
        for item in items:
            if item['name'] == doc_name:
                doc_id = item['id']
                break
        if doc_id:
            docs_service = build('docs', 'v1', credentials=creds)
            text = input("Please enter the text you would like to add to the document: ")
            requests = [
                {
                    'insert_text': {
                        'location': {
                            'index': 1
                        },
                        'text': '\n' + text + '\n'
                    }
                }
            ]
            result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
            print(f"{text} has been added to {doc_name}.")
            continue
        else:
            print(f"No document found with name {doc_name}. Please try again.")
            continue
    elif action == "Quit":
        print("Exiting program.")
        exit()
    else:
        print("Invalid input. Please choose from: NewDocument, EditDocument, or Quit.")
