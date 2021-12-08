# Scripts for monitoring storage
Directories might have to be changed.

# Mailing.ps1
This script extracts storage information from the disks on the computer/server it's running on.

By default it extracts data from every disk that has a name. 
You can exclude disks by adding it in a list in the $excludedDisks variable in the script.

It extracts the disks name, used storage in %, used storage in GB, free storage in GB, health status and operational status. 
Then it saves this data to an CSV.

At the end it sends the storage information as an email with the CSV attached. 
There are variables that contains the senders password and email, as well as the SMTP server, recepients email adress, theme, and the content.

# parseEmail.py

