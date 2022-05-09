def XmlAttri2Dict(el, targetDict)->dict:
    for index,key in enumerate(el.keys()):
        if not (key =='flags' or key=="{http://www.w3.org/2001/XMLSchema-instance}type"):
            targetDict[key] = el.items()[index][1]
    
    return targetDict

def ParseError(el, targetDict)->dict:
    targetDict['Event ID'] = el[0].items()[0][1]
    targetDict['Severity'] = el[0].items()[1][1]
    targetDict['Error source'] = el[0].items()[2][1]
    return targetDict
    

def ParseExtAndOutcome(el, targetDict, error)->dict:
    index = 0
    if error: index = 1
    targetDict['StepType'] = el[index][0][0].text
    targetDict['StepGrp'] = el[index][0][1].text
    targetDict['BlockLevel'] = el[index][0][2].items()[0][1]
    targetDict['Index'] = el[index][0][3].items()[0][1]
    try:
        targetDict['TotalTime'] = el[index][0][4].items()[0][1]
    except:
        targetDict['LoopIndex'] = el[index][0][4][0].items()[0][1]
        targetDict['TotalTime'] = el[index][0][5].items()[0][1]
        
    try:
        targetDict['ModuleTime'] = el[index][0][5].items()[0][1]
    except:
        targetDict['ModuleTime'] = targetDict['TotalTime']

    
    targetDict['Outcome'] = el[index+1].items()[0][1]
    
    return targetDict

def ParseTestResultDetails(el, targetDict)->dict:
    try:
        targetDict['ResultDataType'] = el.items()[1][1]
        targetDict = XmlAttri2Dict(el[0][0], targetDict)

        if not 'value' in targetDict:
            targetDict['value'] = el[0][0][0].text

        targetDict['LimitComparator'] = el[1][0][0].items()[0][1]
        if targetDict['LimitComparator']=='EQ':
            targetDict['LimitType'] = 'Expected'
            targetDict['LimitValue'] = el[1][0][0][0][0].text
        elif targetDict['LimitComparator']=='AND':
            targetDict['LimitType'] = 'LimitPair'
            limitIndex = 0
            if 'nonStandardUnit' in targetDict.keys():
                limitIndex = 1
            if el[1][0][0][0].items()[0][1] == 'GE':
                targetDict['LowerLimit'] = el[1][0][0][0][0].items()[limitIndex][1]
                targetDict['UpperLimit'] = el[1][0][0][1][0].items()[limitIndex][1]
            else:
                targetDict['LowerLimit'] = el[1][0][0][1][0].items()[limitIndex][1]
                targetDict['UpperLimit'] = el[1][0][0][0][0].items()[limitIndex][1]
    except:
        pass
    
    return targetDict

def CsvWriteDict(f, srcDict):
    for key in srcDict.keys():
        f.write("%s, %s\n" % (key, srcDict[key]))
