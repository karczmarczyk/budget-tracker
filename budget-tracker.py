import sys

csvSeparator = ";"

def stopWithMessage (message):
    print ("ERROR: "+message)
    sys.exit()

def readBudgetPlan (src):
    budgetPlanFile = open(src, "r")
    t = {}
    lineNr = 1
    for line in budgetPlanFile:
        lineT = line.strip().split(csvSeparator)
        if (len(lineT) == 0):
            print ("skip empty line nr "+str(lineNr))
            continue
        if (len(lineT) != 2):
            stopWithMessage("Line nr "+str(lineNr)+" has wrong number of columns")
        name = lineT[0]
        try:
            value = float(lineT[1])
        except ValueError:
            stopWithMessage("Value in line "+str(lineNr)+", \""+str(lineT[1])+"\" is not a number")
        if name in t:
            stopWithMessage("Duplicate entry in budget plan in line nr "+str(lineNr))
        
        t[name] = value    
        lineNr = lineNr + 1
            
    budgetPlanFile.close()
    print ("Budget plan: "+src+" loaded.")
    return t

def readExpenseListFile (src):
    expenseListFile = open(src, "r")
    t = []
    lineNr = 1
    for line in expenseListFile:
        lineT = line.strip().split(csvSeparator)
        if (len(lineT) == 0):
            print ("skip empty line nr "+str(lineNr))
            continue
        if (len(lineT) != 3):
            stopWithMessage("Line nr "+str(lineNr)+" has wrong number of columns")
        name = lineT[0]
        try:
            value = float(lineT[1])
        except ValueError:
            stopWithMessage("Value in line "+str(lineNr)+", \""+str(lineT[1])+"\" is not a number")
        date = lineT[2]
        
        t.append({'name': name, 'value': value, 'date': date})
        lineNr = lineNr + 1

    expenseListFile.close()    
    print ("Expense list: "+src+" loaded.")
    return t

def aggregator (budgetPlan, expenseList):
    t = {}
    temp = {
        'category': 'all',
        'budget':0,
        'costs': 0,
        'difference': 0,
        'entries': 0,
        'unique_days': 0,
        'when_exceeded': ''
    }
    t['all'] = temp

    for budgetName in budgetPlan:
        temp = {
            'category': budgetName,
            'budget':budgetPlan[budgetName],
            'costs': 0,
            'difference': 0,
            'entries': 0,
            'unique_days': 0,
            'when_exceeded': ''
        }
        t[budgetName] = temp
        t['all']['budget']+= budgetPlan[budgetName]

    for item in expenseList:
        itemName = item['name']
        if itemName in t:
            t[itemName]['category'] = itemName
            t[itemName]['costs']+= item['value']
            t[itemName]['difference'] = t[itemName]['budget'] - t[itemName]['costs']
            t[itemName]['entries']+=1
            if t[itemName]['when_exceeded']=="" and t[itemName]['difference']<=0:
                t[itemName]['when_exceeded'] = item['date']

            t['all']['costs']+= item['value']
            t['all']['difference'] = t['all']['budget'] - t['all']['costs']
            t['all']['entries']+=1
            if t['all']['when_exceeded']=="" and t['all']['difference']<=0:
                t['all']['when_exceeded'] = item['date']
        else:
            print ("WARNING: Expense \""+itemName+"\" not found on budget list. SKIP")   
        
    return t

def getHeader ():
    return {'category':"str",'budget':"float",'costs':"float",'difference':"float",'entries':"int",'unique_days':"int",'when_exceeded':"date"}

def cell (str, width):
    return str.ljust(width)

def displayResult (summary):
    print("")
    width = 20
    lineH = ""
    for header in getHeader():
        lineH+=cell(header,width)
    print(lineH)
    
    for lineName in summary:
        line = ""
        for header in getHeader():
            line+= cell(str(getFormattedCellValue(summary[lineName][header], getHeader()[header])),width)
        print (line)
    print("")

def makeOutputFile (summary, summaryFileName):
    f = open(summaryFileName, "w")
    f.write(makeCsv(summary))
    f.close()

def makeCsv (input):
    csvLines = []
    csvLines.append(csvSeparator.join(getHeader()))
    for lineName in input:
        line = []
        for header in getHeader():
            line.append(str(getFormattedCellValue(input[lineName][header], getHeader()[header])))
        csvLines.append(csvSeparator.join(line))
    return "\n".join(csvLines) 

def getFormattedCellValue (value, type):
    match type:
        case 'float':
            value = numberFormat(value)

    return value


def numberFormat (number):
    return '{:.2f}'.format(number)

#############################################################################

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print ("usage: "+sys.argv[0]+" budget_plan expense_list [summary_file]")
    sys.exit()

budgetPlanFileName = sys.argv[1]
expenseListFileName = sys.argv[2]

if len(sys.argv) == 4:
    summaryFileName = sys.argv[3]

budgetPlan = readBudgetPlan (budgetPlanFileName)
expenseList = readExpenseListFile (expenseListFileName)

summary = aggregator (budgetPlan, expenseList)

displayResult (summary)

if len(sys.argv) == 4:
    print ("Result saved in "+summaryFileName+".")
    makeOutputFile (summary, summaryFileName)

print("")
