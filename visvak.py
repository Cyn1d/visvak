import sys
import datetime
from datetime import date
from datetime import timedelta
from os import remove

def main():
    args = sys.argv[1:] #all the system arguments

    today = date.today() #todays date
    todaystr = today.strftime("%d%m%y")
    try:
        data = open('data.txt', 'r+') #open the data file
        data.close()
    except:
        try:
            if args[0] == '-init':
                init()
                return
        except:
            nofilefound()
            return
    if len(args) == 0:
        print("No arguments supplied. do 'python3 visvak.py -help'.")
        return
    else:
        defaultDistribution = intitaliseDefaults()
        dispach(args, defaultDistribution, todaystr)
        return


def dispach(args, defaultDistribution, todaystr):
    if args[0] == '-help':
        dispachhelp()
        return
    elif args[0] == '-add':
        distribution = args[-1]
        try:
            if distribution.startswith('[') and distribution.endswith(']'):
                distribution = inputDistributionParser(distribution)
                for i in range(len(distribution)):
                    distribution[i] = int(distribution[i])
            else:
                distribution = False
        except:
            print('Invalid argument.Only numbers allowed.')
            return
        if args[-1][-1] == ']':
            point = -1
        else:
            point = len(args)
        topic = ' '.join(args[1:point]).lower() # topic = ' '.join(args[1:-1]).lowercase()
        dispachadd(topic, distribution, defaultDistribution) #call dispachadd with parsed arguments.
        return
    elif args[0] == '-list':
        dispachlist()
        return
    elif args[0] == '-todo':
        dispachtodo(todaystr)
        return
    elif args[0] == '-info':
        topic = ' '.join(args[1:]).lower()
        dispachinfo(topic, todaystr)
        return
    elif args[0] == '-default':
        dispachdefault(defaultDistribution)
    elif args[0] == '-remove':
        topic = ' '.join(args[1:]).lower()
        dispachremove(topic)
    else:
        print("Invalid argument. do 'python3 visvak.py -help' to see all commands.")
        return



def dispachadd(topic, distribution, defaultDistribution):
    data = findTopicInDataTXT(topic)
    if data:
        print("Topic already exists. To know how to delete a topic check 'python3 visvak.py -help'.\n")
    else:
        file = open('data.txt', 'a')
        if distribution:
            parsedDates = distributionToDateStr(distribution)
            file.write(topic + '|' + removeQuotesFromDates(parsedDates) + '\n')
        else:
            parsedDates = distributionToDateStr(defaultDistribution)
            file.write(topic + '|' + removeQuotesFromDates(parsedDates) + '\n')
        file.close()
        print("{} successfully added!".format(topic))
    return


def dispachlist():
    data = open('data.txt', 'r')
    line = data.readline()
    line = data.readline()
    i = 1
    while line != '':
        topic = line[:line.find('|')]
        print(str(i)+". "+topic)
        i += 1
        line = data.readline()
    print("Done.")
    data.close()
    return



def dispachtodo(todaystr):
    data = open('data.txt', 'r')
    line = data.readline()
    line = data.readline()
    todayTopics = []
    while line != '':
        topic = line[:line.find('|')]
        dates = dateStrToDateStrList(line[line.find('|')+1:-1])
        for i in dates:
            if i == todaystr:
                todayTopics.append(topic)
                break
        line = data.readline()
    data.close()
    count = 1
    if len(todayTopics) == 0:
        print("Nothing for today!")
        return
    for j in todayTopics:
        print("{}. {}".format(str(count), j))
        count += 1
    return


def dispachremove(topic):
    if topic == '':
        print("Invalid request.")
        return
    data = findTopicInDataTXT(topic)
    if data:
        responce = input("Are you sure you want to delete {} from database[yes/no]\n".format(topic)).lower()
        acceptable_responces = ['yes', 'yeah', 'y', 'no', 'nah', 'nope', 'n']
        while(responce not in acceptable_responces):
            print("Invaild responce.")
            responce = input("Are you sure you want to delete {} from database[yes/no]\n".format(topic)).lower()
        if responce == "y" or responce == "yes":
            replaceLineInFile(topic, None)
            print("Done.")
        else:
            return
    else:
        print("{} not found in database.".format(topic))




def dispachinfo(topic, todaystr):
    topicFromData = findTopicInDataTXT(topic)
    if topicFromData:
        dates = dateStrToDateStrList(topicFromData[1])
        for i in dates:
            rslt = dateCompare(todaystr,i) #i and todaystr are both strings in format ddmmyy
            if rslt[0] == 1:
                print("Next revision for {} in {} day(s).".format(topic, (rslt[2]-rslt[1]).days))
                return
            if rslt[0] == 0:
                print("Revision for {} is today!\n".format(topic))
                return
    else:
        print("Topic not found!")
        return


def dispachhelp():
    print("-todo :usage 'python3 visvak.py -todo'. list all the topics you need to rewise today.")
    print("-add :usage 'python3 visvak.py -add <topic name> <distribution>'. Example: '-add sicp [1,2,3,6,10]' .If no list is provided distribution is assumed to be default.")
    print("-list  :usage 'python3 visvak.py -list' . lists all the topic names in the database.")
    print("-default :usage 'python3 visvak.py -default'. Prints the default day distribution.")
    print("-remove :usage 'python3 visvak.py -remove <topic name>'. Removes the topic from the data base.")
    print("-info :usage 'python3 visvak.py -info <topic name>' .Gives the next revision date of the topic.")
    return



def removeQuotesFromDates(parsedDates): #takes in a list with string items. string format: ddmmyy
    temp = '['
    for i in range(len(parsedDates)):
        temp += parsedDates[i]
        if i != len(parsedDates)-1:
            temp += ', '
    temp += ']'
    return temp



def dateCompare(date1, date2): #returns 1 if d2>d1, returns 2 if d1>d2, returns 0 if d1 == d1. date1 and date2 are strings in formate ddmmyy
    date1 = datetime.datetime(day = int(date1[:2]), month = int(date1[2:4]), year = int(date1[4:]))
    date2 = datetime.datetime(day = int(date2[:2]), month = int(date2[2:4]), year = int(date2[4:]))
    if date2 > date1:
        return [1,date1,date2]
    elif date1 > date2:
        return [2,date1,date2]
    else:
        return [0,date1,date2]

def replaceLineInFile(topic, replacement):
    file = open('data.txt', 'r+')
    lines = file.readlines()
    file.close()
    try:
        remove('./data.txt')
    except:
        print('Error: missing permissions. In order to delete a topic from data.txt, visvak deletes and writes a new data.txt.')
        return
    file = open('data.txt', 'a+')
    if replacement == None:
        for i in lines:
            if i.startswith(topic):
                pass
            else:
                file.write(i)
    else:
        for i in lines:
            if i.startswith(topic):
                file.write(replacement)
            else:
                file.write(i)


def inputDistributionParser(strlist):
    last = ''
    lst = []
    last_taken = 0
    for i in strlist[1:-1]:
        if i == ',' or i == ' ':
            if last_taken == 1:
                lst.append(last)
            last_taken = 0
            last = ''
        else:
            last += i
            last_taken = 1
    return lst



def distributionToDateStr(unparseddate): #unparsd dates is a list of ints.
    today = date.today()
    dates = []
    for i in unparseddate:
        new = today + timedelta(days = int(i))
        dates.append(new.strftime("%d%m%y"))
    return dates  # return a list with strings in format ddmmyy




def findTopicInDataTXT(topic):
    data = open('data.txt', 'r')
    line = data.readline() #extra readline so as to skip the first line, it contains the default distribution.
    line = data.readline()
    while line != '':
        linetopic = line[:line.find('|')]
        if linetopic == topic:
            dates = line[line.find('|')+1:-1]
            return [linetopic, dates]
        line = data.readline()
    return False



def dateStrToDateStrList(datestr): #convert the datestr into a list which contains str of the format ddmmyy
    firstpass = datestr[1:-1].split(', ') #firstpass = ', '.split(datestr[1:-1])
    return firstpass







def intitaliseDefaults():
    data = open('data.txt', 'r')
    defaultdistri = data.readline()[1:-1]
    data.close()
    lst = defaultdistri[:-1].split(", ")
    for i in range(len(lst)):
        lst[i] = int(lst[i])
    return lst

def dispachdefault(defaultDistribution):
    print("The default distribution for visvak is:")
    print(defaultDistribution)


def init():
    try:
        file = open('data.txt', 'w')
        file.write("[2, 3, 5, 7, 11, 17, 25, 38, 57, 86, 129, 194, 291, 437]\n")
        file.close()
        print("Welcome to cyan1de's visvak program. Name comes from VISmarama(meaning forgetting) and VAKrata(meaning curve), coincidentally visvak also means sage in sanskrit, which imo the program is.")
        print("Very simple remainder program which uses Ebbinghaus Forgetting Curve principle.")
        print("You enter a topic and an input say 'sicp' is the topic and [2,3,10,18,40] is the input data.")
        print("lets say the date you entered the topic is x, the program will remind you on, x+2, x+3, x+10(aka 10 days after you first studied the topic) etc..")
        print("All the data is stored in the data.txt so dont delete it.")
        print("The program contains a default date distribution, type 'python3 visvak.py -help' to see how to use this program and also check/modify the default distribution.")
    except:
        print("Cannot create the data file. possible permission error. Try moving the program to another location.")
    return


def nofilefound():
    print("""No data file found.\nMake sure you have initialised the program.
do 'python3 visvak.py -init' to run the initialisation process. Its a one
time process and not to be repeated.\n""")
    return





if __name__ == '__main__':
    main()
