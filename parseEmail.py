import imaplib
import email
from email.header import decode_header
import os, time, shutil
import pandas as pd # pip install pandas
import logging
import re
import pymysql
import csv

logging.basicConfig(level=logging.INFO, filename="log", filemode="a+",
                                    format="%(asctime)s : %(levelname)s : %(message)s")


# Connects to database
db = pymysql.connect(
    host="localhost",
    user="root", 
    password="Test123", 
    database="testing"
)
cursor = db.cursor()

# Replaces spaces with _ in a string
def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)


# account credentials
username = "akstestm@gmail.com"
password = "TestMail1234"

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")

# authenticate
imap.login(username, password)


imap.list()
imap.select("inbox")

n=0
(retcode, messages) = imap.search(None, '(UNSEEN)')

# Creates a directory for the attachments if there is none
if not os.path.exists("downloadedAttachments"):
    os.makedirs("downloadedAttachments")
    logging.info("Created directory downloadedAttachments")

# Reads all unread emails
if retcode == 'OK':
    
    # Runs once for every unread email
    for i in messages[0].split():
        print("Processing")
        logging.info("Processing")
        n=n+1

        # fetch the email message by ID
        res, msg = imap.fetch(i, "(RFC822)")
        for response in msg:  
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)

            # Get server and customer name using regex. 
            serverSearch = "storageInfo (.*?)\ server"
            customerSearch = "server (.*?)\ customer"
            serverName = re.search(serverSearch, str(subject)).group(1)
            customerName = re.search(customerSearch, str(subject)).group(1)

            for part in msg.walk():
                # extract content type of email
                contentDisposition = str(part.get("Content-Disposition"))
                if "attachment" in contentDisposition:
                    # download attachment
                    fileName = part.get_filename()
                    logging.info(f"Downloaded attachment {fileName}")
                    if fileName:
                        # Directory to save the attachments to
                        folderName = f"downloadedAttachments/{clean(subject)}"
                        if not os.path.isdir(folderName):
                            # makes a folder for this email (named after the subject)
                            os.mkdir(folderName)
                            logging.info(f"Created directory {folderName}")
                        filePath = os.path.join(folderName, fileName)
                        # download attachment and save it
                        open(filePath, "wb").write(part.get_payload(decode=True)) 

        try: 
            # Directory of where the CSV is located
            df = pd.read_csv(f"downloadedAttachments/{clean(subject)}/storageInfo.csv",
            na_values = ["not available", "n.a."], sep =";", encoding="UTF-16 LE") # Unnecessary 
            print(f"Server: {serverName}" )
            print(f"Customer: {customerName}")

            # Inserts customer name, if the customer name already exists in the db it won't be inserted.
            cursor.execute(f"INSERT INTO customertable (customerName) VALUES ('{customerName}') ON DUPLICATE KEY UPDATE customerId=customerId+0")

            # Inserts server name, if the server name already exists in the db it won't be inserted. 
            cursor.execute(f"INSERT INTO servertable (serverName, customerId) SELECT '{serverName}', customertable.customerId FROM customertable ORDER BY customerId DESC LIMIT 1 ON DUPLICATE KEY UPDATE serverId=serverId+0")


            # Open unformatted csv file
            df = pd.read_csv(f"downloadedAttachments/{clean(subject)}/storageInfo.csv",
                        na_values = ["not available", "n.a."], sep =";", encoding="UTF-16 LE")


            # Clean column names
            df.columns = [x.replace(" ", "").replace("(", "").replace("%", "").replace("GB", "").replace(")", "") for x in df.columns]

            # Replace datatypes
            replacements = {
                "object": "varchar",
                "float64": "varchar"
            }
            colStr = ", ".join("{} {}".format(n, d) for (n, d) in zip(df.columns, df.dtypes.replace(replacements)))

            # Saves to new csv
            df.to_csv("storageInfo.csv", header=df.columns, index=False, encoding="utf-8")

            # Opens new formatted csv file
            csv_data = csv.reader(open("storageInfo.csv"), )

            # Skips the first row containing the headers
            header=next(csv_data)

            # Inserts the storage data for every row into the db
            for row in csv_data:
                cursor.execute("INSERT INTO storagetable (diskName, usedStorage, totalStorage, freeStorage, healthStatus, operationalStatus, serverId) SELECT %s, %s, %s, %s, %s, %s, servertable.serverId FROM servertable ORDER BY serverId DESC LIMIT 1", row)

            print("Importing data")
            print("\nData added successfully\n")

        except OSError:
            print(f"\nError! No folder called {clean(subject)} exists!\n")
            logging.info(f"Error! No folder called {clean(subject)} exists!")


imap.close()
imap.logout()

db.commit()
db.close()


# Delete files or directories older than 2 days
twoDaysAgo = time.time() - (2 * 86400)
root = "downloadedAttachments"


for i in os.listdir(root):
    path = os.path.join(root, i)

    if os.stat(path).st_mtime <= twoDaysAgo:
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"Removed file {path}")
            except:
                print("Could not remove file:", i)

        else:
            try:
                shutil.rmtree(path)
                print(f"Removed directory {path}")
            except Exception:
                print("Could not remove directory:", i)

