#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#############################################################################
##                                                                         ##
## qradar.py: a dummy QRadar XML export parser                             ##
## Copyright (C) 2018  jme@acklabs.net                                     ##
##                                                                         ##
#############################################################################

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Import
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import re
import ast
import sys
import json
import getopt
import fnmatch
import base64
from lxml import etree
import xml.etree.ElementTree as et


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Variables
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start_dir       = ""                # Start directory
verbose         = False             # Verbose is off by default
tagToSearch     = 'payloadAsBase64' # Default Tag to search
decode          = False             # Do we try and decode the string in BAS64?
listOfTags      = {}                # Dictionnary where we store parsed tags
doListe         = False             # Should we display the list ?
searchURL       = False             # Should we try (I insist on try) to find URLS in the tag?
urls            = []                # List of urls

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## Functions
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_file(filename, num_line, pattern):
    regex = re.compile(pattern)
    num_line -= 1    #Line number start at 0
    try:
        with open(filename) as f:
            line = f.readlines()[num_line]
            if(regex.match(line)):
                return True
            else:
                return False
    except:
        print("Error in function check_file()")
        pass

def file_search(start_dir):
    try:
        for root, dirs, files in os.walk(start_dir):
            for file in files:
                #print('found file :', file)
                if (fnmatch.fnmatch(file, '*.xml') and check_file(os.path.join(root, file), 2, "<EventList>")):
                    if (verbose):
                        print('Found qradar file at: '),
                        print(os.path.join(root, file))
                    #file_to_parse = os.path.join(root, file)
                    parse_flasback(os.path.join(root, file))

    except Exception as e:
        print("Critical error while parsing directory")
        print(e)
        sys.exit(2)

def not_implemented(option):
    print("Option %s not implemented yet (woopsie)." % (option))
    sys.exit()

def usage():
    print("# QRadar.py: a crappy QRadar export display tool")
    print("# (c) 2018 Orange/DSCS/ITNSEC under the BSD License.")
    print("Usage: ./qradar.py DIRECTORY [Options]")
    print("Options:")
    print("-v, --verbose=            Verbose mode (duh)")
    print("-t, --tag=                Specify which tag to dump. Default is ",tagToSearch)
    print("-l, --list=               Liste tags found in the xml files")
    print("-d, --decode=             Try to base64 decode the tag value")
    print("-u, --url                 Try extract URL strings from the tag")

    
    #~~~~~~~~~~~~~~ Parse Flasback Files ~~~~~~~~~~~~~~
def parse_flasback(filename):
    if (verbose):
        print("Entering qradar parsing")
    parser = etree.XMLParser(encoding="utf-8", recover=True) #Initialise the xml parser
    Flashback = et.parse(filename, parser=parser)            #Try to recover from bad              
    root = Flashback.getroot()                               # xml files
    # -- Contstruct a dictionnay of XML tags
    for Element in root.iter():
        if (Element.tag in listOfTags):
            listOfTags[Element.tag] += 1
        else:
            listOfTags[Element.tag] = 1

        currentTagValue = Element.text
        if (Element.tag == tagToSearch and not doListe):
            if (decode):
                try:
                    currentTagValue = base64.b64decode(Element.text)
                    if (searchURL):
                        urls = []
                        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', currentTagValue.decode('utf-8'))
                except:
                    pass
            if (searchURL):
                    for i in urls:
                        print(i)
            else:
                print(currentTagValue)
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##
##                          Main program  ➭❤️
##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    #~~~~~ Argument parsing
    try:
        start_dir = sys.argv[1]
    except: #If no argument was passed then we display the help and exit.
        usage()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[2:],
            "hs:a:vlit:du",
            ["help", "search=", "attr=", "verbose", "list", "ioc=", "tag=", "decode", "url"]
            )
    except getopt.GetoptError: # print help information and exit
        usage()
        sys.exit(2)
    #~~~~~ 
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-v", "--verbose"):
            verbose = True
        if o in ("-l", "--list"):
            doListe = True
        if o in ("-v", "--verbose"):
            verbose = True
        if o in ("-t", "--tag"):
            tagToSearch = a
        if o in ("-d", "--decode"):
            decode = True
        if o in ("-u", "--url"):
            searchURL = True      
    #~~~~~
    file_search(start_dir)
    if (doListe):
        print('=== BEGIN KEYWORD LIST ===')
        for i in listOfTags:
            print(i)
        print('=== END KEYWORD LIST ===')
    if (verbose):
        print("    ⤷ All done")



