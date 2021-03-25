#!/usr/bin/python3

# small script to monitor ssh logins and notify via twitter

# based on example https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import re
import argparse

import platform
hostname = platform.uname()[1]

log_pat = r'^(\w{3} \d{1,} \d{1,}:\d{1,}:\d{1,}) (.*?) sshd.*?: (Invalid|Connection closed|Accepted|Disconnected).*?(?:user|for) (.*?) (?:from| )? ?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port (.*?)[ |\n](?:\[(.*?)\])?'

class SSHMonitor:
    length = 0

    def __init__(self, auth_log, length):
        self.watch_file = auth_log
        self.length = length
        self.observer = Observer()

    def run(self):
        event_handler = Handler()

        self.observer.schedule(event_handler, self.watch_file)
        self.observer.start()

        try:
            #have inf loop
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Stopped observer")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.event_type == "modified":
            log = Path(event.src_path)
            newlen = log.stat().st_size
            with log.open() as f:
                f.seek(watch.length)
                # out = f.read()
                for line in f:
                    # print(line.strip())
                    match = re.findall(log_pat, line)
                    # print(match)
                    ssh_stage = ""
                    if match:
                        group = match[0]
                        if group[2] == "Disconnected":
                            action_type = "disconnected from"

                        elif group[2] == "Accepted":
                            action_type = "connected to"
                        elif group[2] == "Connection closed":
                            action_type = "connection closed"
                            ssh_stage = " during "+group[6]
                        elif group[2] == "Invalid":
                            action_type = "bad user login attempt!"
                        else:
                            action_type = "unknown"
                        msg = "User {}@{}:{} {} {} at {}" \
                            .format(group[3], group[4], group[5], action_type+ssh_stage, hostname, group[0])
                        message(msg)
                    # print(match)
                watch.length = newlen

def message(msg):
    print(msg)
    if args.twitter:
        api.PostDirectMessage(msg, twitter_id)
    if args.output:
        with open(args.output, 'a+') as f:
            f.write(msg+"\n")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Monitor")

    # parser.add_argument('required', action="store", help="Required Variable")
    parser.add_argument('-l', '--auth_log', dest="auth_log", action="store", default="/var/log/auth.log", help="Log file to monitor")
    parser.add_argument('-o', '--output', dest="output", action="store", help="Output log location")
    parser.add_argument('-t', '--twitter', dest="twitter", action="store", help="Path to twitter api keys")

    args = parser.parse_args()

    if args.twitter:
        import twitter
        import json
        tw_conf = Path(args.twitter)
        if tw_conf.exists():
            with tw_conf.open() as f:
                data = json.loads(f.read())
                api_key = data['api_key']
                api_secret_key = data['api_secret_key']
                access_token = data['access_token']
                access_token_secret = data['access_token_secret']
                twitter_id = data['twitter_id']
                api = twitter.Api(consumer_key=api_key,
                                                consumer_secret=api_secret_key,
                                                access_token_key=access_token,
                                                access_token_secret=access_token_secret)
        else:
            sys.exit("Error loading twitter config")


    print("Starting watch")
    auth_log = Path(args.auth_log)
    if auth_log.exists():
        with auth_log.open() as f:
            length = len(f.read())
    else:
        sys.exit("Error loading log file")
    # with open(
    watch = SSHMonitor(auth_log, length)
    watch.run()


#TODO check how this works when ipv6
