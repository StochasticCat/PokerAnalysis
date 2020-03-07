import datetime
import re
from decimal import Decimal
import os

global gplayeractions   #T2556089874
global collectioncount
global disregardCashout
collectioncount = 0
disregardCashout = True

dataStr = ""  
filecount = 1
directory = '//Users/macbookpro/Downloads/f00l00' #SMOKEDACES: CHANGE THISO SO THAT IT SPECIFIES THE DIRECTORY  YOUR FILES ARE IN
print ('Reading data from txt.')
for root, dirs, files in (os.walk(directory)):
    '''for name in files:
        if '+' in name: 
            #print ('This is filename:')
            print (name)
            pass'''
    print (dirs)
    if dirs == []:
        dirs = [directory]
    for name in dirs:
        diras = os.path.join(root, name)      #SMOKEDACES: CHANGE THIS SO THAT IT SPECIFIES THE DIRECTORY YOUR TXT FILES ARE IN.
        for filename in os.listdir(diras):
            if ".txt" in filename:
                if '+' in filename:
                    print('File {} is a tournament file. Discard.'.format(filename))
                else:
                #print (filecount)
                    filecount += 1
                    f = open(diras + "/" +filename, "r", encoding='utf-8')
                    dataStr += f.read()
                    f.close()
                    '''if 'lnexorable collected $107.40 from pot' in dataStr:
                        print ('this is the filename', filename)
                        print ('and the filecount is', filecount)
                    if '_tHMWNN_ collected $7.60 from pot' in dataStr:
                        print ('my filename is', filename)'''
print ('Data read.')
#dataStr = dataStr.replace('lnexorable','Inexorable')
print ('Total {} files'.format(filecount))
dataArrTmp = re.split('PokerStars Hand #|PokerStars Zoom Hand #',dataStr)
print ('We have {} hands in total.'.format(len(dataArrTmp)))
dataArr = []
print ('Populating data array...')
for i in dataArrTmp:
    dataArr.append(i.split("\n"))
print ('Data array obtained.')
trueData = []


def seatSrc(x, maxSeat):
    tmp = []
    for i in x[2:(3 + int(maxSeat))]:
        if ("Seat " in i):
            namewords = i.split()[2:-3] #take from second (name) element excluding last 3, that will be '($x in chips)'
            name = namewords[0] #the first word of a name
            if len(namewords) > 1: #if there is more than one word in the name
                for j in namewords[1:]: #iterate through namewords from second to last
                    name += ' ' #add a space to the current name
                    name += j   #and the following word of the name
            tmp.append(name)
    return tmp


def zaidejuVeiksmai(x, maxSeat, usersList):
    tmp = {}
    cc = 1
    rake = 0
    #print (x)
    for i in x:
        if len(i) == 0:
            break
        '''if "| Rake " in i:  # we changed it from summary to get rake for every hand to check correctness
            #rake = get_amount(i)
            break'''
        cc += 1
    for j in usersList:  # TODO: need to make this street by street, mindind the FLOP,TURN,RIVER separators (4 streets)
        tmp[j] = []
        streetactions = []  # actions taken on a given street
        for i in x[:(cc - 1)]:
            # print (i)
            if ' said ' in i or ' said,' in i:  #### Disregard all the lines of people saying stuff #TODO consider that 'said' could be part of the name
                pass
            else:
                if 'FLOP' in i or 'TURN' in i or 'RIVER' in i:
                    tmp[j].append(streetactions)
                    streetactions = []
                elif j in i:  #####look if a particular username is in line of iterable
                    streetactions.append(i)
        tmp[j].append(streetactions)

    return tmp, rake


def susumavimas(xDic):
    tmp = {}
    for i in xDic:
        tmp[i] = 0
        for j in xDic[i]:
            pass


def calculatePlayerProfitPerStreet(playeractions):  # takes in a list of player's actions
    '''#TODO: iterate from the end until found 'raises' and add it. if encounter 'calls' while iterating add that also (whether 'raises' is found or not). Add all instances of 'calls' found this way. 
If no raise is found, iterate anew until found 'bets', and add bet amount.
Otherwise leave default (0). 
  
 (EXPLANATION: on second iteration, any 'calls' present is already added as we did not find 'raises' and went through the whole list. As a 'calls' action cannot precede a 'bets' action, we should not worry about overcounting. As in case there are no 'bets' actions we should just take all 'calls' actions, we cover that in the first iteration). '''
    profit = 0
    global gplayeractions
    global blinds
    global collectioncount
    global disregardCashout
    gplayeractions = playeractions
    posts = False
    if len(playeractions) > 1 and 'posts small & big blinds' in playeractions[1]:  # TODO make stake specific
        posts = True
    if (len(playeractions) > 1 and 'posts the ante' in playeractions[1]):
        profit -= get_amount(playeractions[1])
    elif (len(playeractions) > 2 and 'posts the ante' in playeractions[2]):
        profit -= get_amount(playeractions[2])
    collection = False #flag to see if a player has already collected money from pot
    for i in reversed(playeractions):
        # print ('lets look at', i, 'shall we?')
        i = i.strip(' and is all-in')
        if ' collected' in i and not 'collected (' in i: #and not collection: #if this is the first instance of collection
            #print (i, collectioncount)
            # print (get_amount(i.strip(' from pot')))
            i = i.strip(' from pot')
            i = i.strip(' from main pot')
            i = i.strip(' from side pot')
            profit += get_amount(i)
            collection = True
            collectioncount += 1
        elif '(pot not awarded as player cashed out)' in i and disregardCashout:
            #print (i)
            
            #print (cashout)
            try: 
                cashout = float(cashout[1:])
                cashout = Decimal(cashout)
                profit += cashout
                #print (profit)
                #print (playeractions)
            except:
                print ('Badly formatted cashout line.')
        elif 'cashed out the hand for' in i and not disregardCashout:
            print (i)   
            #print (cashout)
            try:
                cashout = re.findall("([$£€]\d+.\d+|[$£€]\d+)", i)[0]
                cashout = float(cashout[1:])
                cashout = Decimal(cashout)
                profit += cashout
                #print (profit)
                #print (playeractions)
            except:
                print ('Badly formatted cashout line.')
        elif 'Uncalled bet' in i:
            i = i[:i.rindex(')')]
            profit += get_amount(i)  # now look at loss (investment) cases
        elif ' calls ' in i:  # if the action is a call
            profit -= get_amount(i)
        elif ' raises ' in i:  # if the action is a raise
            raiseSize = get_amount(i)
            if posts:
                raiseSize += blinds[0]
            return Decimal(profit) - Decimal(raiseSize)
        elif ' bets ' in i:  # if the action is a bet
            betSize = get_amount(i)
            return profit - betSize
        elif ' posts small ' in i or ' posts big blind ' in i:
            betSize = get_amount(i)
            return profit - betSize
    return profit  # this is only executed if the only player actions were calling, checking and folding


def last_currency_sign_at(action):
    if action.rfind('$') != -1:
        return action.rfind('$')
    if action.rfind('€') != -1:
        return action.rfind('€')
    if action.rfind('£') != -1:
        return action.rfind('£')
    print ('we are struggling to find a currency sign in', action)
    return 0

def get_amount(i):  # gets money amount from a string that ends with it
    # print (i)
    global gplayeractions
    pos = last_currency_sign_at(i) + 1 #position of first digit after last currency sign
    # print (pos)
    counter = 0
    for j in i[pos:]:  # determine how many digits follow after last currency sign
        if j.isdigit() or j == '.':
            counter += 1
        else:
            break
    try:
        y = Decimal(i[pos:pos + counter])
    except:
        print ('we have trouble with item:', i, 'position and counter is', pos, counter)
        print (gplayeractions)
        return 0
    return Decimal(i[pos:pos + counter])


def calculatePlayerProfitPerHand(playerActionsInHand):  # actually, there should be a net loss equal to rake amount.
    total = 0
    for street in playerActionsInHand:
        total += calculatePlayerProfitPerStreet(street)
    return total

def outputData(trueData):  # should output the hand properties, the list of players in the hand and their profit
    output = []
    print ('Generating internal output from processed data.')
    # print ('this is true data my man', trueData)
    #counter = 0
    for i in trueData:
        #if counter < 20:
            #print ('look at line my man')
            #print (i)
            #counter += 1
        hand = []
        stake = i[0]
        handid = i[-1]
        global blinds
        # print ('we are looking at hand', i)
        blinds = [get_amount(stake[:(last_currency_sign_at(i[0]))]), get_amount(stake)]
        hand.append(i[0])  # gametype + stakes + currency
        hand.append(i[1])  # date (taken out of the list)
        hand.append(i[2])  # how many players max per table?
        playerprofits = []
        for player in i[3]:  # iterate through a list of players, adding [name+profit] to the hand
            profit = [player]
            playeractions = i[4].get(player)  # look at the dictionary value of this player's actions
            add = calculatePlayerProfitPerHand(playeractions)
            profit.append(add)
            playerprofits.append(profit)
        hand.append(playerprofits)
        hand.append(handid)
        output.append(hand)
    return output


# regexRastiPinigam = "([$€]\d+.\d+)"

#discount = 0
#water = 1
#tempprint = 0
print ('Start of data processing')
for i in dataArr:
    #tempprint += 1
    tmp = []
    count = 0
    if (len(i) > 3):  # and count < 10:
        count += 1
        try: 
            tmp.append(re.findall("(:[ a-zA-Z0-9\W\S]+-)", i[0])[0].replace(": ", "").replace(" -", "").strip())
        except:
            print ('The error is with this:')
            print (i)
        tmp.append(re.findall("(\d{4}[\W\S]\d{2}[\W\S]\d{2} \d{1,2}:\d{2}:\d{2})", i[0]))
        #if discount < 100: 
            #print (tmp[1])
            #if len(tmp[1]) < 1:
                #print ('Date parsing error')
                #print (i)
                #print (discount)
                #discount += 1
            #else:
                #if water <= 20:
                    #water +=1
        tmp.append(re.findall("(\d)", i[1])[0])
        tmp.append(seatSrc(i, tmp[2]))
        appending = (zaidejuVeiksmai(i, tmp[2], tmp[3]))
        tmp.append(appending[0])
        tmp.append(appending[1])
        tmp.append(re.findall("^(\d+).*",i[0])[0])
        '''if water < 20:
            print ((re.findall("^(\d+).*",i[0])))
            print (tmp)'''
        trueData.append(tmp)
print ('trueData generated.')

playeractions = trueData[0][4]
allUsers = {}
minid = 1 #the minimum value of player ID
idx = minid
print ('Computing output data.')
finalData = outputData(trueData)
print ('assigning IDs to users')
for i in finalData: #creates a dictionary of all users with assigned IDs
    for j in i[3]:
        if j[0] not in allUsers:
            allUsers[j[0]] = idx
            idx += 1
print ('these are all the users and their IDs')
print (allUsers)
            

colNames =  '''Hand_id\tdate\tgame\tid (users)\tid\tmoney\tseats\tuser_name''' 


file1 = open("pokerdataflowsdisregardcashout.csv","w")#write mode
file1.write(colNames + "\n")
counter = 0
stulpNr = 1
print ('Data processing over. Start of export to csv.')
for i in finalData:
    counter += 1
    if counter % 50000 == 0:
        print ('Exporting hand number ', counter)
    if (len(i) > 0):
        try:
            date = str(i[1][0].strip())
        except:
            date = str(i[1])[1:-1]
        handid = i[-1]
        linestart = handid + '\t' + date + '\t' + str(i[0].strip()) + '\t'
        seats = str(i[2]).strip() 
        for j in i[3]:
            username = j[0]
            money = str(j[1]) 
            userid = str(allUsers.get(username))
            idrecord = str(stulpNr)
            stulpNr += 1
            line = linestart + userid + '\t' + idrecord + '\t' + money + '\t' + seats + '\t' + username 
            file1.write(str(line) + "\n")
file1.close()
print ('Export to csv finished.')
