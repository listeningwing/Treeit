#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
#   ______           _ __
#  /_  __/______ ___(_) /_
#  / / / __/ -_) -_) / __/
# /_/ /_/  \__/\__/_/\__/
# High performance directory compare and merge.
# * Note:
# a. the scripting interface assume input file and data encoded with utf-8.
# b. all data and file output from app side was encoded with utf-8.
#


import re
import json
import os,sys
import locale
import codecs
import random
import string
import subprocess
import base64
import atexit
import signal
from datetime import datetime

app = "/Applications/Treeit.app/Contents/MacOS/Treeit"
inputSources = None # catch ctrl+c

cmdDir = None      # scripting support directory
rootUrls = None    # accessible folders in the list of settings
accesscode = "***" # access code for automation scripts
                   # current ignored

noArgCmd = """
{
  \"msgtype\": \"%s\",
  \"accesscode\": \"%s\",
}
"""


def decodeB64Data(string):
    text = ""
    try:
        decodedBytes = base64.b64decode(string)
        text = str(decodedBytes, "utf-8")
    except: pass
    return text


def runCommand(cmd):
    global app
    dict = None
    lines = []
    isJSON = False

    JSON_message_begin = "_______BEGIN__JSON__MESSAGE_______"
    JSON_message_end   = "_______END____JSON__MESSAGE_______"

    a = []
    a.append(app)
    a.append("-c")
    a.append(cmd)
    proc = subprocess.Popen(a, stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = line.decode('utf-8')
        line = line.rstrip()
        line = re.sub("\s+", " ", line)
        if isJSON:
            if line.startswith(JSON_message_end): isJSON = False
            else: lines.append(line)
        else:
            if line.startswith(JSON_message_begin): isJSON = True
            else: print('%s\n' % line) # normal log message
    textBlock = '\n'.join(lines)
    try:
        dict = json.loads(textBlock)
    except:
        print(textBlock) # print raw message if stdout does not
                         # contain a well-formatted json block
    return dict


def cmdMoveFile(path, reverse):
    global cmdDir
    assert(cmdDir is not None)
    command = None
    filename = os.path.basename(path)
    destpath = "%s/%s" % (cmdDir, filename)
    if reverse:
        if os.path.exists(destpath):
            command = 'mv "%s" "%s"' % (destpath, path)
    else:
        if os.path.exists(path):
            command = 'mv "%s" "%s"' % (path, destpath)
    if command is not None: os.system(command)


def moveFileToAccessible(path):
    cmdMoveFile(path, False)


def moveBackFile(path):
    cmdMoveFile(path, True)


def removeFile(path):
    command = 'rm -rf "%s"' % path
    os.system(command)


def exit_handler(message):
    global inputSources
    if inputSources is not None:
        for file in inputSources:
            moveBackFile(file)
    inputSources = None
    sys.exit(0) # Exit the program after cleanup


def signal_handler(sig, frame):
    exit_handler("exit")


def getCommandDir():
    global noArgCmd, accesscode
    dir = None
    cmd = noArgCmd % ("cmddir", accesscode)
    dict = runCommand(cmd)
    if dict is None: return None
    if dict["result"] == "true":
        dir = dict["file"]
        if not os.path.exists(dir):
            print("Error, '%s' does not exist." % dir)
            dir = None
    return dir


# Row Format:
#     id + status + type + extension + size + modified + path
# type:
#     +: added
#     -: removed
#     O: can't do a overwrite operation, the file was conflicted with target file or folder.
#     M: this file was modified comparing with the target file.
#     R: this file should be renamed, it was conflicted with target file, content is different.
#     D: duplicated file in source folder or target folder.
# extension: extension name of the file
# size: readable file size
# modified: file last modified datetime
# path: full path of the file
# Find duplicates in source folder
def findDuplicates(source):
    global accesscode, inputSources
    boilerplate = """
    {
      \"msgtype\": \"duplicates\",
      \"accesscode\": \"%s\",
      \"source\": \"%s\"
    }
    """

    if not os.path.exists(source):
        print("Error, '%s' does not exist." % source)
        return False

    # ensure accessible
    srcname = os.path.basename(source)
    moveFileToAccessible(source)
    inputSources = []
    inputSources.append(source)
    try:
        cmd = boilerplate % (accesscode, source)
        dict = runCommand(cmd)
    except KeyboardInterrupt: pass
    except: pass
    finally:
        moveBackFile(source)
        inputSources = None
    if dict is None: return None
    if dict["result"] == "true": return dict["data"]
    return None


# Row Format:
#     id + status + type + extension + size + modified + path
# type:
#     +: added
#     -: removed
#     O: can't do a overwrite operation, the file was conflicted with target file or folder.
#     M: this file was modified comparing with the target file.
#     R: this file should be renamed, it was conflicted with target file, content is different.
#     D: duplicated file in source folder or target folder.
# extension: extension name of the file
# size: readable file size
# modified: file last modified datetime
# path: full path of the file
def compareDir(source, target, checkDuplicate):
    global accesscode, inputSources
    boilerplate = """
    {
      \"msgtype\": \"comparedir\",
      \"accesscode\": \"%s\",
      \"source\": \"%s\",
      \"target\": \"%s\",
      \"checkDuplicate\": \"%d\"
    }
    """

    if not os.path.exists(source):
        print("Error, '%s' does not exist." % source)
        return False
    if not os.path.exists(target):
        print("Error, '%s' does not exist." % target)
        return False

    # ensure accessible
    srcname = os.path.basename(source)
    moveFileToAccessible(source)
    tgtname = os.path.basename(target)
    moveFileToAccessible(target)
    inputSources = []
    inputSources.append(source)
    inputSources.append(target)
    try:
        check = 1 if checkDuplicate else 0
        cmd = boilerplate % (accesscode, source, target, check)
        dict = runCommand(cmd)
    except KeyboardInterrupt: pass
    except: pass
    finally:
        moveBackFile(source)
        moveBackFile(target)
        inputSources = None
    if dict is None: return None
    if dict["result"] == "true": return dict["data"]
    return None


# Merge Strategy
# 1. Always overwrite
# 2. Keeping the newest
# 3. Keep both
#
# renameTarget: 0 or 1, default is 1, means rename conflicted target item instead of source.
# dontKeepingAnymore: 0 or 1, move file instead of copy.
# Row indicator in log file:
# ✓: successfully merged in target folder.
# ✗: failed to merge in target.
# ✓+N: successfully merged in target folder with a new file name.
#
def mergeDir(source, target, strategy, renameTarget, dontKeepingAnymore, jsonFile):
    global accesscode, inputSources
    boilerplate = """
    {
      \"msgtype\": \"mergedir\",
      \"accesscode\": \"%s\",
      \"source\": \"%s\",
      \"target\": \"%s\",
      \"strategy\": \"%d\",
      \"renameTarget\": \"%d\",
      \"dontKeepingAnymore\": \"%d\",
      \"dataFile\": \"%s\"
    }
    """

    if not os.path.exists(jsonFile):
        print("Error, '%s' does not exist." % jsonFile)
        return None

    # ensure accessible
    dict = None
    srcname = os.path.basename(source)
    moveFileToAccessible(source)
    tgtname = os.path.basename(target)
    moveFileToAccessible(target)
    datafile = os.path.basename(jsonFile)
    moveFileToAccessible(jsonFile)
    
    inputSources = []
    inputSources.append(source)
    inputSources.append(target)
    inputSources.append(jsonFile)
    try:
        cmd = boilerplate % (accesscode, source, target, strategy, renameTarget, dontKeepingAnymore, datafile)
        dict = runCommand(cmd)
    except KeyboardInterrupt: pass
    except: pass
    finally:
        moveBackFile(source)
        moveBackFile(target)
        moveBackFile(jsonFile)
        inputSources = None
    if dict is None: return None
    if dict["result"] == "true":
        temp = dict["file"]
        if os.path.exists(temp):
            logname = os.path.expanduser('~') + '/Desktop/' + os.path.basename(temp)
            os.system("mv \"%s\" \"%s\"" % (temp, logname))
            return logname
    return None


def testDuplicate(source):
    checkDuplicate = False
    dict = findDuplicates(source)
    if not dict: return None
    # array of array
    for row in dict:
        print(row)

    # writing to json file
    dt = datetime.now()
    name = dt.strftime("%Y_%m_%d_%H_%M_%S.json")
    jsonFile = os.path.expanduser('~') + '/Desktop/' + name
    with open(jsonFile, "w") as outfile:
        json.dump(dict, outfile)
    return jsonFile
    

# Step 1
def testCompare(source, target):
    checkDuplicate = False
    dict = compareDir(source, target, checkDuplicate)
    if not dict: return None
    # array of array
    for row in dict:
        print(row)
    
    # writing to json file
    dt = datetime.now()
    name = dt.strftime("%Y_%m_%d_%H_%M_%S.json")
    jsonFile = os.path.expanduser('~') + '/Desktop/' + name
    with open(jsonFile, "w") as outfile:
        json.dump(dict, outfile)
    return jsonFile

# Step 3
def testMerge(source, target, dontKeepingAnymore, jsonFile):
    renameTarget = 1 #rename conflicted target
    strategy = 2  #keeping the newest
    # jsonFile: must a valid json file
    # jsonFile = os.path.expanduser('~') + '/Desktop/result.json'
    
    logFile = mergeDir(source, target, strategy, renameTarget, dontKeepingAnymore, jsonFile)
    print(logFile)


# Step 2
# inspect JSON file from the result of compare operation,
# compare file or folder one by one, filter some rows, and make
# a new file that have same format from compare operation and then
# call mergeDir().
def inspectJson(jsonFile):
    with open(jsonFile, 'r') as file:
        dict = json.load(file)
        for row in dict:
            # print(row)
            if row[2] == '-': continue # ignore files
            # type = row[3] # filter some type of files
            # filter some records with other conditions
            path = row[-1]
            print(path)
        print(len(dict))
            

def runTests():
    global cmdDir
    cmdDir = getCommandDir()
    if not cmdDir:
        print("Can't get command dir.")
        return
    atexit.register(exit_handler, "atexit called.")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    
    # source = "/Users/yeung/Desktop/Test/x-2016.7.11"
    # jsonFile = testDuplicate(source)
    # print(jsonFile)

    source = "/Users/yeung/Desktop/Test/x-2016.7.11"
    target = "/Users/yeung/Desktop/Test/x-2012.1.4"
    # jsonFile = testCompare(source, target)
    # print(jsonFile)

    jsonFile = "/Users/yeung/Desktop/2025_06_26_13_59_46.json"
    # inspectJson(jsonFile)
    dontKeepingAnymore = 0 # copy file to target
    # merge target into source
    testMerge(source, target, dontKeepingAnymore, jsonFile)


def main():
    runTests()
    

if __name__ == "__main__":
    main()



