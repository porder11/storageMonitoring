# Scripts for monitoring storage
Directories MIGHT need to be changed.

# Mailing.ps1
This script extracts storage information from the disks on the computer/server it's running on.

By default it extracts data from every disk that has a name. 
You can exclude disks by adding it in a list in the $excludedDisks variable in the script.

It extracts the disks name, used storage in %, used storage in GB, free storage in GB, health status and operational status. 
Then it saves this data to an CSV.

At the end it sends the storage information as an email with the CSV attached using gmail SMTP server. 
There are variables that contains the senders password and email, as well as the SMTP server, recepients email adress, theme, and the content.

While using the script at home I need to add -Port 587 in the "Send-MailMessage" command, however when running it at Bazefield this was not necessary. 

# parseEmail.py
This program extracts the data from the email sent using powershell. It extracts the server and customer name from the title, and the storage information from the csv. 
