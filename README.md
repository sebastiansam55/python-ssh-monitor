# SSH monitor

Monitors `/var/log/auth.log` and outputs more readable information. Not feature complete! Don't use for anything important.

## Usage
`python3 main.py -o ssh.log`

Will start the program watching `/var/log/auth.log` by default.

Check the file for implementation details, it uses a rather complicated regex to extract the data.
