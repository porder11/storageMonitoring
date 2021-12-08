$date = Get-Date -Format "dd/MM/yyyy"
$customerName = "A"
$serverName = "Server01" 

$excludeDisks = ""# Discs to be excluded. Seperated by ",". Example: "D", "C", "A"

# Shows discname, total storage, free storage, used storage in %, healthstatus and operationalstatus
$info = Get-Volume | Where { $excludeDisks -notcontains $_.driveletter} |where Driveletter -NotLike ""| Select-Object -Property @{'Name' = 'diskName';Expression= { $_.driveletter }},
@{'Name' = 'usedStorage (%)'; Expression={100 - [math]::round((($_.sizeremaining /1GB) / ($_.size / 1GB))*100, 2)}}, 
@{'Name' = 'totalStorage (GB)';Expression= { [math]::round(($_.size / 1GB), 2) }},
@{'Name' = 'freeStorage (GB)';Expression= { [math]::round(($_.sizeremaining / 1GB), 2) }}, HealthStatus, OperationalStatus


# Creates a CSV containing the storage information.
$csvInfo = $info  | ConvertTo-Csv -Delimiter ";" -NoTypeInformation | Out-File -FilePath ".\storageInfo.csv"#"C:\Users\akselple\Downloads\storageMonitoring\storageInfo.csv"


# Email
$from = "akstestm@gmail.com"
$passwd = ConvertTo-SecureString "TestMail1234" -AsPlainText -Force
$smtp = "smtp.gmail.com"
$recepient = "akstestm@gmail.com"
$theme = "storageInfo $serverName server $customerName customer $date"
$creds = New-Object System.Management.Automation.PSCredential ($from, $passwd)

$content = "Customer name: $customerName", "Server name: $serverName", "Excluded disks: $excludeDisks", $info | Out-String

# Sends an email containing the content aswell as a CSV file.
# Try removing -Port 587 if you are getting an error. I have to use this when I'm on my home WiFi, but not at Bazefield.
Send-MailMessage -To $recepient -From $from -Subject $theme -Body $content -Attachments ".\storageInfo.csv" -SmtpServer $smtp -Credential $creds -UseSsl -Port 587 -DeliveryNotificationOption OnFailure