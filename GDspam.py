import requests
import base64
import itertools
import threading
import time
import json
from os import system

gdspam = 'GD Spam V1'
system(f'title={gdspam}')

THREADS = 10
SUBJECT = "discord.gg/grin"

success_count = 0
error_count = 0
lock = threading.Lock()
stop_event = threading.Event()

def xor(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, itertools.cycle(key)))

def base64_encode(string):
    return base64.urlsafe_b64encode(string.encode()).decode()

def gjp_encrypt(data):
    return base64.b64encode(xor(data, "37526").encode()).decode()

def message_encode(data):
    return base64_encode(xor(data, '14251'))

def upload(account, password, proxy_info, target_id, body):
    global success_count, error_count
    try:
        rr = requests.post("http://www.boomlings.com/database/uploadGJMessage20.php",
                           data={"accountID": account,
                                 "gjp": gjp_encrypt(password),
                                 "toAccountID": target_id,
                                 "subject": base64_encode(SUBJECT),
                                 "body": message_encode(body),
                                 "secret": "Wmfd2893gb7"},
                           headers={"User-Agent": ""},
                           proxies={'http': f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"},
                           timeout=50).text
        if rr == "1":
            with lock:
                success_count += 1
        else:
            with lock:
                error_count += 1
    except requests.exceptions.Timeout:
        with lock:
            error_count += 1

def upload(accounts, passwords, proxy_info, target_id, num_messages, body):
    threads = []
    for i in range(len(accounts)):
        for _ in range(num_messages):
            t = threading.Thread(target=upload, args=(accounts[i], passwords[i], proxy_info, target_id, body))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()
    stop_event.set()

def counters():
    while not stop_event.is_set():
        with lock:
            print("\r\x1b[K", end='')
            print(f"[+] Messages sent: {success_count}\t[-] Errors: {error_count}", end='', flush=True)
        time.sleep(0.1)

def print_title():
    title = r"""
╔═╗╔╦╗  ╔═╗╔═╗╔═╗╔╦╗
║ ╦ ║║  ╚═╗╠═╝╠═╣║║║
╚═╝═╩╝  ╚═╝╩  ╩ ╩╩ ╩
"""
    print(title)

def loadaccounts(config_file):
    with open(config_file, "r") as f:
        config_data = json.load(f)
    accounts = [(acc["id"], acc["password"]) for acc in config_data["accounts"]]
    return accounts

def main():
    global success_count, error_count
    print_title()
    num_messages = int(input("[+] Enter the number of messages: "))
    target_id = input("[+] Enter the target's account ID: ")
    body = input("[+] Enter the message you want to send: ")
    proxy_info = { # Enter proxy server details
        "host": "",
        "port": "",
        "username": "",
        "password": ""
    }
    accounts = loadaccounts("config.json")
    ACCOUNT_IDS, PASSWORDS = zip(*accounts)
    upload_thread = threading.Thread(target=upload, args=(ACCOUNT_IDS, PASSWORDS, proxy_info, target_id, num_messages, body))
    counter_thread = threading.Thread(target=counters)
    upload_thread.start()
    counter_thread.start()
    upload_thread.join()
    counter_thread.join()
    input("\n[+] Press Enter to exit")

if __name__ == "__main__":
    main()
