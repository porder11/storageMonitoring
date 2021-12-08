# Scripts for monitoring storage
Directories MIGHT need to be changed.

## Mailing.ps1
This script extracts storage information from the disks on the computer/server it's running on.

By default it extracts data from every disk that has a name. 
You can exclude disks by adding it in a list in the $excludedDisks variable in the script.

It extracts the disks name, used storage in %, used storage in GB, free storage in GB, health status and operational status. 
Then it saves this data to an CSV.

At the end it sends the storage information as an email with the CSV attached using gmail SMTP server. 
There are variables that contains the senders password and email, as well as the SMTP server, recepients email adress, theme, and the content.

While using the script at home I need to add -Port 587 in the "Send-MailMessage" command, however when running it at Bazefield this was not necessary. 

## parseEmail.py
This program extracts the data from the email sent using powershell and inserts it into a database using pymysql. It extracts the server and customer name from the title, and the storage information from the csv. 

To connect to the database there are certain credentials needed that are stored in variables within the code, this will have to be changed. 

The program creates a directory for the attachments to be downloaded into, if it doesn't already exist.

It automatically reads every unread email in the inbox. This could cause a problem if there are emails that haven't been read but has nothing to do with the storage information. A possible solution might be to create a new inbox where the storage information emails are automatically sent/redirected to.

It replaces spaces with _ in the title and then creates a folder within the "downloadedAttachments" folder created earlier containing the CSV from the email. Then the CSV is opened and cleaned for spaces, special charecters etc and saved to a new CSV. Then it opens the new CSV and extracts and inserts the storage data into the database. It extracts the server and customer name from the title of the email using regex. 

If the server or customer name already exists it will not insert again. HOWEVER the storage data has no check for duplicates. 

The program prints some of the information to the screen so the user can know if the data was added successfully, in addition it creates a log file. These are can be removed without effecting anything else. 
