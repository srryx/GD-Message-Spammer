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

class MessageSender:
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def xor(self, data, key):
        return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, itertools.cycle(key)))

    def base64_encode(self, string):
        return base64.urlsafe_b64encode(string.encode()).decode()

    def gjp_encrypt(self, data):
        return base64.b64encode(self.xor(data, "37526").encode()).decode()

    def message_encode(self, data):
        return self.base64_encode(self.xor(data, '14251'))

    def upload_message(self, account, password, proxy_info, target_id, body):
        try:
            rr = requests.post("http://www.boomlings.com/database/uploadGJMessage20.php",
                               data={"accountID": account,
                                     "gjp": self.gjp_encrypt(password),
                                     "toAccountID": target_id,
                                     "subject": self.base64_encode(SUBJECT),
                                     "body": self.message_encode(body),
                                     "secret": "Wmfd2893gb7"},
                               headers={"User-Agent": ""},
                               proxies={'http': f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"},
                               timeout=50).text
            if rr == "1":
                with self.lock:
                    self.success_count += 1
            else:
                with self.lock:
                    self.error_count += 1
        except requests.exceptions.Timeout:
            with self.lock:
                self.error_count += 1
        finally:
            if self.success_count + self.error_count == self.num_messages * len(self.accounts):
                self.stop_event.set()

    def send_messages(self, accounts, proxy_info, target_id, num_messages, body):
        self.accounts = accounts
        self.num_messages = num_messages
        threads = []
        for account in accounts:
            for _ in range(num_messages):
                t = threading.Thread(target=self.upload_message, args=(account["id"], account["password"], proxy_info, target_id, body))
                t.start()
                threads.append(t)
        for t in threads:
            t.join()

    def counters(self):
        while not self.stop_event.is_set():
            with self.lock:
                print("\r\x1b[K", end='')
                print(f"[+] Messages sent: {self.success_count}\t[-] Errors: {self.error_count}", end='', flush=True)
            time.sleep(0.1)

def print_title():
    title = r"""
╔═╗╔╦╗  ╔═╗╔═╗╔═╗╔╦╗
║ ╦ ║║  ╚═╗╠═╝╠═╣║║║
╚═╝═╩╝  ╚═╝╩  ╩ ╩╩ ╩
"""
    print(title)

def load_accounts(config_file):
    with open(config_file, "r") as f:
        config_data = json.load(f)
    return config_data["accounts"]

def main():
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
    message_sender = MessageSender()
    accounts = load_accounts("config.json")
    threading.Thread(target=message_sender.send_messages, args=(accounts, proxy_info, target_id, num_messages, body)).start()
    threading.Thread(target=message_sender.counters).start()
    message_sender.stop_event.wait()
    print("\n[+] Press Enter to exit")
    input()

if __name__ == "__main__":
    main()
