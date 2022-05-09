__author__ = "Harry, Hu Yu"
__copyright__ = "Copyright 2022, APS SEO @ Keysight"
__credits__ = ["Harry, Hu Yu"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Harry, Hu Yu"
__email__ = "harry.hu@keysight.com"
__status__ = "Alpha - for PoC"

# -*- coding: utf-8 -*-
"""
This module is created at the purpose of parsing xml format data from GES Venture for FCT testers

input: xml(gb2312) folder
output: csv(UTF-8)

Point of interests

1. Parsing xml format data
2. Understanding of FCT data structure
3. extract useful information
4. Some tests data format is different from others, which needs special processing

"""

import sys
from time import sleep
import xml.etree.ElementTree as ET
import os
from gesXmlParsingfunc import XmlAttri2Dict, ParseExtAndOutcome, ParseError, ParseTestResultDetails, CsvWriteDict
from ProgressBar import printProgressBar

    # PARSE GES XML FILE
def xml2CSV(path):
    
    #create csv file path
    pre, ext = os.path.splitext(path)
    newPath=pre+'.csv'

    csvF = open(newPath, 'w')

   #read xml file 
    with open(path,'rb+') as a:
        data = a.read().decode('gb2312')
        tree = ET.ElementTree(ET.fromstring(data))

    #parse xml into tree element, formating the tree elements
    testResults = tree.getroot()[0]

    #Parsing operator meta information
    oprXML = testResults[0][0]
    operator = dict.fromkeys([])
    operator = XmlAttri2Dict(oprXML, operator)

    #print(operator)
    #print('Writing operator data to %s file'%newPath)
    CsvWriteDict(csvF, operator)

    resultSetXML = testResults[1]

    resultSetMetaInfo = dict.fromkeys([])
    resultSetMetaInfo = XmlAttri2Dict(resultSetXML,resultSetMetaInfo)
    error = False
    stepIndex = 2
    if 'Event' in resultSetXML[0].tag:
        #print('Error Event Detected')
        error = True
        stepIndex = 3
        resultSetMetaInfo = ParseError(resultSetXML[0], resultSetMetaInfo)


    resultSetMetaInfo = ParseExtAndOutcome(resultSetXML, resultSetMetaInfo, error)
    #print(resultSetMetaInfo)
    #print('Writing Step Meta info data to %s file'%newPath)
    CsvWriteDict(csvF, resultSetMetaInfo)

    
    stepInfo = []
    for index, step in enumerate(resultSetXML[stepIndex:]):
        stepInfo.append(XmlAttri2Dict(step,dict.fromkeys([])))
        stepInfo[index]['Tag'] = step.tag.split('}')[1]
        error = False
        if 'Event' in step[0].tag:
            error = True
            stepInfo[index] = ParseError(step[0], stepInfo[index])
        stepInfo[index] = ParseExtAndOutcome(step, stepInfo[index], error)
        try:
            stepInfo[index] = ParseTestResultDetails(step[2],stepInfo[index])
        except:
            pass

    #print('Creating csv Header row')
    allKeys = []
    for eachStepinfo in stepInfo:
        for eachdictKey in eachStepinfo.keys():
            if not eachdictKey in allKeys:
                allKeys.append(eachdictKey)
                csvF.write("%s, "%eachdictKey)

    csvF.write("\n")


    #print('Writing step data to %s file'%newPath)
    
    for eachStepinfo in stepInfo:
        for key in allKeys:
            if key in eachStepinfo.keys():
                csvF.write("%s, "%eachStepinfo[key])
            else:
                csvF.write("N.A, ")
        csvF.write("\n") 

def workOnfolder(folderName)->list:
    totalXmlFiles = 0
    for file in os.listdir(folderName):
        if file.endswith(".xml"):
            totalXmlFiles+=1

    currentXmlFileIndex = 0

    printProgressBar(currentXmlFileIndex, totalXmlFiles, prefix = '%d Xml Files Processed:'%currentXmlFileIndex, suffix = 'Complete', length = 50)

    for index, file in enumerate(os.listdir(folderName)):
        if file.endswith(".xml"):
            xmlName = os.path.join(folderName, file)
            xml2CSV(xmlName)
            currentXmlFileIndex+=1

            preStr = 'Total %d Files'%totalXmlFiles
            suStr = ' %d files Processed'%currentXmlFileIndex

            printProgressBar(currentXmlFileIndex, totalXmlFiles, prefix = preStr, suffix = suStr, length = 50)

def main():
    if len(sys.argv)==1:
        print('No folder name provided')
    else:
        workOnfolder(str(sys.argv[1]))




if __name__ == "__main__":
    main()
