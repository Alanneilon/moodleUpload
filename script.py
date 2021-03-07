from requests import get, post
import json
from dateutil import parser
import datetime
import os
import re

# Module variables to connect to moodle api:
# Insert token and URL for your site here.
# Mind that the endpoint can start with "/moodle" depending on your installation.
KEY = "8cc87cf406775101c2df87b07b3a170d"
URL = "https://034f8a1dcb5c.eu.ngrok.io"
ENDPOINT = "/webservice/rest/server.php"


def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict == None:
        out_dict = {}
    if not type(in_args) in (list, dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict


def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update(
        {"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    # print(parameters)
    response = post(URL+ENDPOINT, data=parameters).json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response
#################################################################################################################
def getNoFromFolder(filelist):
#function to extract numbers from folder and filenames
    wkno=[]
    for i in range(0, len(filelist)):
        print(filelist[i])
        #extract number from each file name in the list
        wk=re.findall('[0-9]+', filelist[i])
        #display the number
        print(wk)
        #add the number to a list that will store just the numbers
        wkno.extend(wk)
    return wkno
##################################################################################################################
def convertStringToInt(stringList):
#function to convert the numbers from the files names to an int, as they are caputured as string
    n = 0
    while n < len(stringList):
        stringList[n] = int(stringList[n])
        n += 1
        #return the list of integers
    return(stringList)
####################################################################################################################################################################################################################
def updateLinks(wkno):
    #assemble the links and link names that will go in the summary of each required section
    summaryList=[]
    for i in range(0, len(wkno)):
        no=wkno[i]
        # using place holders to implant the numbers(stored as string) into the links
        summary="<a href=\'https://mikhail-cct.github.io/ooapp/wk{}/#\'>Week {}: Data types</a><br><a href=\"https://mikhail-cct.github.io/ca3-test/wk{}.pdf\">Week {}: Modules.pdf</a>".format(no,no,no,no)
        # assing the summary links and names to a new list and then return it to the caller        
        summaryList.append(summary)
    return summaryList
####################################################################################################################################################################################################################
def updateAllSec(courseid,data,wknum,sumList):
#function to update all required summary sections that match the incoming sectionid with links 
    for i in range(0, len(wknum)):
        data[0]['summary'] = sumList[i]
        data[0]['section'] = wknum[i]
        # writing the links each section one at a time until loop completes
        sec_write = LocalUpdateSections(courseid, data)

####################################################################################################################
def getLocalDirItems():
# function to get a list of items in the local directory
    filelist=os.listdir()
    print(filelist)
    return filelist

######################################################################################################################
# Rest-Api classes
#####################################################################################################################
class LocalGetSections(object):
    """Get settings of sections. Requires courseid. Optional you can specify sections via number or id."""

    def __init__(self, cid, secnums=[], secids=[]):
        self.getsections = call('local_wsmanagesections_get_sections',
                                courseid=cid, sectionnumbers=secnums, sectionids=secids)
###################################################################################################################

class LocalUpdateSections(object):
    """Updates sectionnames. Requires: courseid and an array with sectionnumbers and sectionnames"""

    def __init__(self, cid, sectionsdata):
        self.updatesections = call(
            'local_wsmanagesections_update_sections', courseid=cid, sections=sectionsdata)

######################################################################################################################

courseid = "17"  # id of course required to be updated

# Get all sections of the course.
sec = LocalGetSections(courseid)

#  Assemble the payload
data = [{'type': 'num', 'section':0 , 'summary': '', 'summaryformat': 1, 'visible': 1 , 
'highlight': 0, 'sectionformatoptions': [{'name': 'level', 'value': '1'}]}]

# Output readable JSON, but print only summary
print(json.dumps(sec.getsections, indent=4, sort_keys=True))
#get list of local folders and files
filelist=getLocalDirItems()
#extract a number from the name of the folders and files
wkno=getNoFromFolder(filelist)
#print a list of the numbers from the names of the files
print(wkno)  
#convert the numbers on the list extracted from the file names to int
wknum=convertStringToInt(wkno)
#print the list of int that will set the section id's
print(wknum)
#assemble the summarysummaries with the required links that match the section id's
sumList=updateLinks(wkno)
#display the links assembled
print(sumList)
#update the sections on the website with the summaries that match the required section number
updateSec=updateAllSec(courseid,data,wknum,sumList)
#obtain the newly updated section information
sec = LocalGetSections(courseid)
#display the latest section information
print(json.dumps(sec.getsections, indent=4, sort_keys=True))




