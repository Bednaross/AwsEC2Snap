# AwsEC2Snap
This project takes snapshots of EC2 instances.  It uses boto3 to connect to AWC account and performs snapshot of your VMs.

##Configuring

Configure your own AWS cli profile by running:
`aws configure  --profile snap `

##Running

`pipenv run “python snap/snap.py”` 
