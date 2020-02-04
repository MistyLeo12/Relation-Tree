'''
Created on Sep 27, 2019

@author: Victoria Wu vlw9
'''

# from __future__ import unicode_literals
import csv
from difflib import SequenceMatcher
import copy
import math
import operator
import response
import random
from datetime import datetime
import time
# import csv, unicodedata
    
start_time = 0

def processFile(file):
    '''
    takes csv file and returns a dictionary 
    id:[full name, first name, surname now, 
    surname at birth, gender, deceasedY/N, 
    mother ID, mother name, father ID, 
    father name, partner ID, ex-partner, 
    birth year, birth month, birth day,
    death year, death month, more...]
    '''
    ret = {}
    csvf = open(file, encoding='utf-8')
    freader = csv.reader(csvf,delimiter=';')
    next(freader)
    for row in freader:
        data = row[0].split(",")
        ret[data[0]] = data[1:]
    return ret

def get_partners(whole_dic):
    '''
    input is a dictionary, the result of a call to processFile
    id:[partner1, partner2, etc.] where partner means current
    and previous partners, if any
    '''
    d = {}
    for (k,v) in whole_dic.items():
        d[k] = v[12].split() #IDs of ex-partner(s), if any
        if v[10] != "":      #if person does have current partner
            d[k].append(v[10])   #ID of current partner
    return d
    
def toInt(val):
    '''
    Used to change empty birth years to 0. needs to be int to sort later
    '''
    if val == '':
        return 0
    return int(val)
    
def child_dic(whole_dic):
    '''
    takes in the big data dictionary
    returns a dictionary
    key is parent (str), value is list of childrenID and their birthyears in form (ID, year) - (list of tuples)
    '''
    d = {}
    for (k,v) in whole_dic.items():
        mother = v[6]
        father = v[8]
        if mother != "":
            if mother not in d:
                d[mother] = [(k, toInt(v[13]))]
            else:
                d[mother].append((k, toInt(v[13])))
        if father != "":
            if father not in d:
                d[father] = [(k, toInt(v[13]))]
            else:
                d[father].append((k, toInt(v[13])))
    return d

def child_noYear(whole_dic):
    '''
    returns a dictionary
    key is parent (str), value is list of children by ID 
    used in queries that don't return many results, and therefore
    do not require sorting by birth years
    '''
    d = {}
    for (k,v) in whole_dic.items():
        mother = v[6]
        father = v[8]
        if mother != "":
            if mother not in d:
                d[mother] = [k]
            else:
                d[mother].append(k)
        if father != "":
            if father not in d:
                d[father] = [k]
            else:
                d[father].append(k)
    return d
    

def name_to_id(file):
    '''
    takes csv file and returns a dictionary 
    of name:id. If name is not unique,
    name:num followed by name1:"id",
    etc. for all of name. these are in
    the form namex:[id, birth year] where x
    is the ith time that name shows up
    '''
    d = {}
    years = {}
    csvf = open(file, encoding='utf-8')
    freader = csv.reader(csvf,delimiter=';')
    next(freader)
    for row in freader:
        data = row[0].split(",")
        if data[1] not in d:
            d[data[1]] = data[0]
            years[data[1]] = data[14]
        else:
            if isinstance(d[data[1]], str): #first time encountering duplicate
                d[data[1]+"1"] = [d[data[1]], years[data[1]]] #earlier encounter
                d[data[1]] = 1
            num = d[data[1]]
            d[data[1]+str(num+1)] = [data[0], data[14]]
            d[data[1]] += 1

    print(len(d))
    return d

def sizeGen(lst):
    '''
    lst is a list of lists
    just a visual to see how the generation size changes over time
    in theory size of generations grows by 2^n, but the higher up in the tree, the less likely
    there will be data
    '''
    ret = []
#     count = -2
    for i in lst:
        ret.append(len(i))
    return ret

def oneGenderLine(data, ret, gender):
    '''
    used to find matrilineal / patrilineal ancestors. Only adds ancestor of corresponding gender to entry
    '''
    if ret[-1] == [0]:
        return ret
    for id in ret[-1]:
        if gender == "F":
            parent = data[id][6]
        elif gender == "M":
            parent = data[id][8]
        if parent != "":
            ret.append([parent])
        else:
            ret.append([0])
    return ret

def buildPrevGen(data, ret):
    '''
    data is a result of a call to processFile()
    ret is the entry that grows with each call, starts as [[<person_id>]]
    builds person's ancestors
    '''
    nextlst = [] 
    if ret[-1] == [0]: #reached root
        return ret
    for id in ret[-1]:
        mother = data[id][6]
        father = data[id][8]
        if mother != "":
            nextlst.append(mother) 
        if father != "":
            nextlst.append(father)
    nextlst = list(set(nextlst)) #remove duplicates
    if len(nextlst) > 0:
        ret.append(nextlst)
    else:
        ret.append([0])
    return ret

def buildNextGen2(data, ret):
    '''
    data is a result of call to child_dic()
    this function is an improvement of buildNextGen (can be found in deprecated.py)
    '''
    if ret[-1] == [0]:
        return ret 
#     print(data[ret[-1][0]])
    nextlst = []
    for i in func(ret[-1]):
        if i in data:
            nextlst += list(set(data[i]))
    nextlst = list(set(nextlst))
#     nextlst = list(set([data[i] for i in ret[-1]]))
    if len(nextlst) > 0:
        ret.append(nextlst)
    else:
        ret.append([0])
   
def func(tup):
    '''
    in a list of tuples, returns a new list of the first element in each tuple
    '''
    #tup = [(1, 2), (3, 4)] -> [1, 3]
    ret = [k for (k,v) in tup]
    return ret
   
def getAncestors(data, id1):
    '''
    not currently used. given an id, returns a list of all of that person's ancestors
    '''
    ret = [[id1]]
    while ret[-1] != [0]:
        buildPrevGen(data, ret)
    ret = ret[1:-1]
    ret = collapse(ret)
    ret =  list(set(ret))
    return ret

def isAncestor(data, id1, id2):
    '''
    id1 is YOUNGER, id2 is OLDER
    if id2 is not an ancestor of id1, return False
    if id2 is ancestor of id1, return True
    returns "done" if id1 and id2 are same person
    '''
    if id1 == id2:
        return "done"
    if id1 == "":
        return False
    ret = [[id1]]
    while ret[-1] != [0]:
        buildPrevGen(data, ret)
        if id2 in ret[-1]:
            return True
    return False

def getIdx(ls, prev):
    '''
    ls is list of lists. let inner be every innerlist of ls. return first index where inner[-1] == prev, -1 otherwise. used in path
    '''
    for i in range(len(ls)):
        if ls[i][-1] == prev:
            return i
#     print("DEBUG")
    return -1

def getIdxPrev(ls, prev):
    '''
    ls is list of lists. let inner be every innerlist of ls. return first index where inner[-2] == prev, -1 otherwise. used in path
    '''
    for i in range(len(ls)):
        if ls[i][-2] == prev:
            return i
#     print("DEBUG")
    return -1
    

def completePrevGen3(data, ret, ancestor):
    '''
    only include ancestors who are descendants of larger ancestor in question
    hoping to not have memory error
    '''
    nextlst = [] 
    for id in ret[-1]:
        if isinstance(id, int):
            mother = id
            father = id
        else:
            mother = data[id][6]
            father = data[id][8]
        if isinstance(mother, str) and mother != "":
            if isAncestor(data, mother, ancestor):
                nextlst.append(mother)
            else:
                mother = 1
        if mother == "":
            if len(nextlst) == 0:
                nextlst.append(1)
            elif isinstance(nextlst[-1], str):
                nextlst.append(1)
            else:
                nextlst[-1] += 1
        elif isinstance(mother, int): #is int
            if len(nextlst) == 0:
                nextlst.append(mother)
            elif isinstance(nextlst[-1], str):
                nextlst.append(mother)
            else:
                nextlst[-1] += mother
        if isinstance(father, str) and father != "":
            if isAncestor(data, father, ancestor):
                nextlst.append(father) 
            else:
                father = 1
        if father == "":
            if len(nextlst) == 0:
                nextlst.append(1)
            elif isinstance(nextlst[-1], str):
                nextlst.append(1)
            else:
                nextlst[-1] += 1
        elif isinstance(father, int):
            if len(nextlst) == 0:
                nextlst.append(father)
            elif isinstance(nextlst[-1], str):
                nextlst.append(father)
            else:
                nextlst[-1] += father
    ret.append(nextlst)
    return ret

def shift(ls, currIndex):
    '''
    ls is a compressed list of strings and ints i.e. ["Abby", "Carol", 2, 3, "Therese", 1]
    uncompressed, ls would look like ["Abby", "Carol", "", "", "", "", "", "Therese", ""]
    given currIndex, which corresponds to the uncompressed ls, return the corresponding index in ls
    i.e. return ls.index(<uncompressedLs>[currIndex]) but more precise, bc not necessarily first occurrence
    in this example, if currIndex is 7 the return value is 4
    (values in ls do not have to be unique)
    '''
    count = -1
    for i in range(len(ls)):
        val = ls[i]
        if isinstance(val, int):
            count += val 
            if count > currIndex:
                return i
        else:
            count += 1
        if count == currIndex:
            return i
    return -1

def path2(data, id1, id2):
    '''
    id1 is YOUNGER, id2 is OLDER
    returns the shortest path(s) from id1 up to id2
    uses completePrevGen2 to save memory
    use completePrevGen3 to save memory AND time
    '''
    if not isAncestor(data, id1, id2):
        return False #mistake has been made, id2 is NOT ancestor of id1
    paths = [[id1]]
    ret = [[id1]]
    while id2 not in ret[-1]:
        completePrevGen3(data, ret, id2)
    ret = ret[1:]
    momWas = False
    for gen in range(len(ret)):
        currIndex = 0
        for individual in range(len(ret[gen])):
            person = ret[gen][individual]
            if isinstance(person, int):
                currIndex += person
            else:
#                 if isAncestor(data, person, id2): #if id2 is an ancestor of person ... with change to cpg3, everyone is now descendant of ancestor
                ind = 0
                if gen == 0 and individual == 0:
                    ind = 0
                    momWas = True
                elif gen == 0 and individual == 1 and momWas:
                    ind = -1
                elif gen != 0:
                    ind = getIdx(paths, ret[gen-1][shift(ret[gen-1], currIndex//2)])
                if ind == -1:
                    ind = getIdxPrev(paths, ret[gen-1][shift(ret[gen-1], currIndex//2)])
                    root = paths[ind][:-1]
                    paths.append(root + [(person, "fresh")])
                else:
                    root = paths[ind]
                    root += [(person, "fresh")]
                currIndex += 1
        for entries in paths:
            entries[-1] = entries[-1][0] #remove the fresh, no longer fresh
#     print(len(paths)) #this is exactly how many ways id1 is descended from id2, is >= length of future return value
    numPaths = len(paths)
    paths = [i for i in paths if i[-1] == id2] #only keep the n closest ways id1 is descended from id2
    reverseInner(paths)
    return paths, numPaths
   
def patMatDict(data, gender):
    '''
    depending on the gender of the individual the user inputs,
    patMatDict creates a patrilineal or matrilineal dictionary of 
    mothers and their daughters or fathers and their sons
    '''
    d = {}
    for (k,v) in data.items():
        if v[4] == gender:
            parent = "" #for the blank genders
            name = ""
            if gender == "F":
                parent = v[6]
                name = v[7]
            elif gender == "M":
                parent = v[8]
                name = v[9]
            if parent != "" and name != "":
                if parent not in d:
                    d[parent] = [(k, v[13])]
                else:
                    d[parent].append((k, v[13]))
    return d
   
def childrenByG(whole_dic, gender):
    '''
    used for data cleaning. if gender is "M", keys is men with children and values is their children.
    if gender is "F", keys is women with children and values is their children
    '''
    d = {}
    for (k,v) in whole_dic.items():
        mother = v[6]
        father = v[8]
#         print(father)
        if gender == "F":
            if mother != "" and mother != '"' and len(mother) == 5:
                if whole_dic[mother][4] == "F": #mother actually is female
                    if mother not in d:
                        d[mother] = [k]
                    else:
                        d[mother].append(k)
        if gender == "M":
            if father != "" and father != '"' and len(father) == 5:
                if whole_dic[father][4] == "M":
                    if father not in d:
                        d[father] = [k]
                    else:
                        d[father].append(k)
    return d
    
def patMatNextGen(data, ret, gender):
    '''
    for females, returns daughters' daughters' daughters...
    for males, returns sons' sons' sons...
    patMat is short for patrilinealMatrilineal
    '''
    if gender == "M":
        i = 8
    elif gender == "F":
        i = 6
    nextlst = []
    if ret[-1] == [0]:
        return ret
    nextlst = list(set([k for (k,v) in data.items() if v[i] in ret[-1]]))
    if len(nextlst) > 0:
        ret.append(nextlst)
    else:
        ret.append([0])

def pick_person(dic, order):
    '''
    prompt the user for person to compare
    dic is a result to a call to name_to_id()
    '''
    d = copy.deepcopy(dic)
    delete = [k for (k,v) in d.items() if isinstance(v, list) == True]
    for k in delete:
        del d[k]
    if order == "one":
        person = input("Pick the first person: > ")
    elif order == "relation":
        person = input("Pick the person: > ")
    else:
        person = input("Pick the second person: > ")
    while person not in d:
        if extract_similar(d, person) == "no sim":
            person = input(person + " could not be found. Try again? > ")
        else:
            if len(extract_similar(d, person)) == 1:
                response = input(person + " could not be found. Did you mean " + print_lines(extract_similar(d, person)) + "? Type yes or no. > ")
                if response == "no":
                        if order == "one":
                            person = input("Try again. Pick the first person: > ")
                        elif order == "relation":
                            person = input("Try again. Pick the person: > ")
                        else:
                            person = input("Try again. Pick the second person: > ")   
                elif response == "yes":
                    person = extract_similar(d, person)[0]
                else:
                    person = response
            else:
                print(person + " could not be found. Did you mean one of the following?")
                print(print_lines(extract_similar(d, person)))
                response = input("Pick one of the above or say no: > ")
                if response == "no":
                    if order == "one":
                        person = input("Try again. Pick the first person: > ")
                    elif order == "relation":
                        person = input("Try again. Pick the person: > ")
                    else:
                        person = input("Try again. Pick the second person: > ")  
                else:
                    person = response
    if isinstance(dic[person], int):
        print("There is more than one " + person + " in this tree. Which best describes the year " + person + " was born?")
        short = extract_years(dic, person)
        year = input(" > ")
        while extract_person_given_year(short, year) == "no":
            print("That was not one of the options. Try again.")
            year = input(" > ")
        id1 = extract_person_given_year(short, year)
        
    else:
        id1 = dic[person]
    return id1, person

def reverseInner(ls):
    '''
    [["a", "c", "b"], ["john", "george", "saxony"]] becomes [["b", "c", "a"], ["saxony", "george", "john"]]
    used to flip to result of path2(). looks better (to me at least) if generations read older -> younger, up -> down
    '''
    for el in ls:
        el.reverse()
    return ls

def direct(data, id1, id2, gen, person1, person2, gender2, mode, birthYear):
    '''
    visualizes a direct relationship, i.e. id1 is a descendant of id2, or vice versa
    mode is completely different from ask()'s mode!! Mode differentiates between calling response1 or response2
    '''
#     tick = datetime.now()

    info = path2(data, id2, id1)
    
#     tock = datetime.now()
#     print(tock-tick)
    
    line = info[0]
    numPaths = info[1]
    if line == False:
        return "WRONG"
    ways = len(line)
    moreWays = numPaths - ways
    if ways > 10:
        line = line[-10:]
    if mode == 2:
        if ways > 1:
            if ways > 10:
                print(response.response2(gen, person1, person2, gender2) + " in " + str(ways) + " ways, but this is a lot, so below are 10 such ways:")
                if moreWays > 0:
                    print("Other than the " + str(ways - 10) + " ways of equal closeness not being shown, " + person2 + " is actually descended from " + person1 + " in " + str(moreWays) + " more unique ways of lesser closeness.")
            else:
                print(response.response2(gen, person1, person2, gender2) + " in " + str(ways) + " ways:")
                if moreWays > 0:
                    print("Note that " + person2 + " is actually descended from " + person1 + " in " + str(moreWays) + " more unique ways; however, these are more distant")
        else:
            print(response.response2(gen, person1, person2, gender2))
            if moreWays > 0:
                print("Note that " + person2 + " is actually descended from " + person1 + " in " + str(moreWays) + " more unique ways; however, these are more distant")
    else:
        if ways > 1:
            if ways > 10:
                print(response.response1(gen, person1, person2, gender2) + " in " + str(ways) + " ways, but this is a lot, so below are 10 such ways:")
                if moreWays > 0:
                    print("Other than the " + str(ways - 10) + " ways of equal closeness not being shown, " + person1 + " is actually descended from " + person2 + " in " + str(moreWays) + " more unique ways of lesser closeness.")
            else:
                print(response.response1(gen, person1, person2, gender2) + " in " + str(ways) + " ways:")
                if moreWays > 0:
                    print("Note that " + person1 + " is actually descended from " + person2 + " in " + str(moreWays) + " more unique ways; however, these are more distant")
        else:
            print(response.response1(gen, person1, person2, gender2))
            if moreWays > 0:
                print("Note that " + person1 + " is actually descended from " + person2 + " in " + str(moreWays) + " more unique ways; however, these are more distant")
    print()
    for ls in line:
        for e in ls:
            print((data[e][0] + " (" + str(birthYear[e]) + ")").center(100))
            if e != ls[-1]:
                print("|".center(100))
        if ways > 1:
            print()
            print("-----------------------------".center(100))
            print()
    return ""

def indirectBody(len1, len2, common, partner1, partner2, line, line2, data, birthYear, mode):
    '''
    takes care of the response when two people have an indirect relationship
    '''
    space = " ---------------------- "
    if len1 >= len2:
        if mode == "half":
#             partner1 = data[partner1][0]
#             partner2 = data[partner2][0]
            left = len(partner1) + len(space) + 1
            right = len(common) + 2 + len(space)
            bar1 = len(partner1) + 2 + len(space) //2
            bar2 = len(common) + 2 + len(space)
            print(partner1 + " " + space + " " + common + " " + space + " " + partner2)
        else:
            space = " " + space.strip() *3 + " "
            [a, b] = common.split(" & ")
            left = len(a) + len(space) // 3
            right = len(space) // 3 * 2
            bar1 = len(a) + len(space) // 6
            bar2 = len(space) // 6 * 4
            print(a + " " + space + " " + b)
            
        # lineData = [data[line[i]][0] for i in range(len(line))][::-1] +[common]
        # line2Data = [data[line2[i]][0] for i in range(len(line2))][::-1] + [common]
        # visualization.constructGraph(lineData, line2Data, data[line[-1]][0], data[line2[-1]][0], common)
        for i in range(len(line)):
            if i < len2:
                print("|".rjust(bar1) + "|".rjust(bar2))
                print((data[line[i]][0] + " (" + str(birthYear[line[i]]) + ")").rjust(left) + (data[line2[i]][0] + " (" + str(birthYear[line2[i]]) + ")").rjust(right))
            else:
                print("|".rjust(bar1))
                print((data[line[i]][0] + " (" + str(birthYear[line[i]]) + ")").rjust(left))
    else: #line2 is longer
        if mode == "half":
            left = len(partner2) + len(space) + 1
            right = len(common) + 2 + len(space)
            bar1 = len(partner2) + 2 + len(space) //2
            bar2 = len(common) + 2 + len(space)
            print(partner2 + " " + space + " " + common + " " + space + " " + partner1)
        else:
            space = " " + space.strip() *3 + " "
            [a, b] = common.split(" & ")
            left = len(a) + len(space) // 3
            right = len(space) // 3 * 2
            bar1 = len(a) + len(space) // 6
            bar2 = len(space) // 6 * 4
            print(a + " " + space + " " + b)
        # lineData = [data[line[i]][0] for i in range(len(line))][::-1] +[common]
        # line2Data = [data[line2[i]][0] for i in range(len(line2))][::-1] + [common]
        # visualization.constructGraph(lineData, line2Data, data[line[-1]][0], data[line2[-1]][0], common)
        for i in range(len(line2)):
            if i < len1:
                print("|".rjust(bar1) + "|".rjust(bar2))
                print((data[line2[i]][0] + " (" + str(birthYear[line2[i]]) + ")").rjust(left) + (data[line[i]][0] + " (" + str(birthYear[line[i]]) + ")").rjust(right))
            else:
                print("|".rjust(bar1))
                print((data[line2[i]][0] + " (" + str(birthYear[line2[i]]) + ")").rjust(left))

def indirectFull(data, id1, id2, person, couple, birthYear):
    '''
    visualizes a relationship in which id1 and id2's closest common ancestor(s) are a couple, as opposed to a singleton
    '''
    line = path2(data, id1, person)[0]
    if line == False:
        return "WRONG"
    line = random.choice(line) #choose a random line, could be from 1 or many choices
    line = line[1:] #remove root, will add both ancestors later
    len1 = len(line)
    
    line2 = path2(data, id2, person)[0]
    if line2 == False:
        return "WRONG" 
    line2 = random.choice(line2)
    line2 = line2[1:]
    len2 = len(line2)
    
    partner1 = ""
    partner2 = "" #don't need these two, not used in full mode
    indirectBody(len1, len2, couple, partner1, partner2, line, line2, data, birthYear, "full")
    return ""

def indirectHalf(onepartner, twopartner, data, id1, id2, person, birthYear):
    '''
    visualizes a relationship in which id1 and id2's closest common ancestor is one person, as id1 and id2 are
    most closely descended from two different partners of this one common ancestor
    person is the closest common ancestor between id1 and id2
    id1 is descended from onepartner and person (all are ids, not names)
    id2 is descended from twopartner and person
    birthYear is a dictionary of ids to birth years, if known, ???? otherwise
    '''
    line = path2(data, id1, person)[0]
    if line == False:
        return "WRONG"
    line = random.choice(line) #choose a random line, could be from 1 or many choices
    line = line[1:] #remove root, will add both ancestors later
    len1 = len(line)
    
    line2 = path2(data, id2, person)[0]
    if line2 == False:
        return "WRONG" 
    line2 = random.choice(line2)
    line2 = line2[1:]
    len2 = len(line2)
    #always put longer line, if any, on left (just personal pref)
    common = data[person][0] + " (" + str(birthYear[person]) + ")"
    partner1 = data[onepartner][0] + " (" + str(birthYear[onepartner]) + ")"
    partner2 = data[twopartner][0] + " (" + str(birthYear[twopartner]) + ")"
    indirectBody(len1, len2, common, partner1, partner2, line, line2, data, birthYear, "half")
    return ""

def calculate(how, gen1, gen2):
    '''
    variable how is type string, either "full" or "half".
    calculates the score of a relationship in order to later choose only the closest one(s)
    '''
    if gen1 == gen2:
        score = gen1 * 2
    else:
        score = (min(gen1, gen2) - 1) * 2 + abs(gen1 - gen2)
    if how == "half":
        return score + 1
    return score
        

def ask(file, mode):
    '''
    ask the user for two people, return how they are related if they are
    '''
    global start_time

    dic = name_to_id(file)
    pick1 = pick_person(dic, "one")
    pick2 = pick_person(dic, "two")
    start_time = time.time()
    id1 = pick1[0]
    id2 = pick2[0]
    person1 = pick1[1]
    person2 = pick2[1]
    data = processFile(file)
    clean(data)
    gender1 = data[id1][4] 
    gender2 = data[id2][4]
    partner_dic = get_partners(data)
    birthYear = yearWithQ(data)
    print() #separates querying the user for input and the later output
    
    if id1 == id2:
        return ("These two are the same person.")
    
    entry1 = buildPrevGen(data, [[id1]])
    entry2 = buildPrevGen(data, [[id2]])
  
#     builds entry all the way to end, visualizes growing and shrinking gen sizes
#     while entry1[-1] != [0]:
#         entry1 = buildPrevGen(data, entry1)
#     print(entry1)
#     return sizeGen(entry1)
    
    while len(set(collapse(entry1))&set(collapse(entry2))) == 0:
        entry1 = buildPrevGen(data, entry1)
        entry2 = buildPrevGen(data, entry2)
    
    common = set(collapse(entry1))&set(collapse(entry2))
    if common == {0}:
        return ("There is currently no known relation between " + person1 + " and " + person2)
    
    common = list(common)
    if id1 in common: #person one is older, is ancestor of person two
        gen1 = 0 
        gen2 = whichGen(id1, entry2)
        if mode == 2:
            return direct(data, id1, id2, gen2, person1, person2, gender2, 2, birthYear)
        return (response.response2(gen2, person1, person2, gender2))
    
    if id2 in common: #person two is older
        gen1 = whichGen(id2, entry1) 
        gen2 = 0
        if mode == 2:
            return direct(data, id2, id1, gen1, person1, person2, gender2, 1, birthYear)
        return (response.response1(gen1, person1, person2, gender2))
    
    if len(common) == 1:
        person = common[0]
        gen1 = whichGen(person, entry1) 
        gen2 = whichGen(person, entry2)
        gens = [gen1, gen2]     
        ancestor = data[person][0]

        if mode == 2:
            print(response.halfRelationship(gens, person1, person2, ancestor, gender1, gender2) + ":") #only going to show one random way, don't need ways
            onepartner = set(entry1[gen1]) & set(partner_dic[person])
            twopartner = set(entry2[gen2]) & set(partner_dic[person])
            onepartner = list(onepartner)[0]
            twopartner = list(twopartner)[0]
            return indirectHalf(onepartner, twopartner, data, id1, id2, person, birthYear)
        return (response.halfRelationship(gens, person1, person2, ancestor, gender1, gender2))
    
    seen = []  #if len(common) > 2, i.e. at least two common ancestors in same generation
    ancestorPairs = []
    for person in common:
        if person not in seen:
            partners = partner_dic[person]
            partnerInCommon = list(set(partners)&set(common))
            if partners == []: #very unlikely, if this is the case than this ancestor had issue by unknown partner
                ancestorPairs.append(["full", person, data[person][0]+" & unknown"])
            elif len(partnerInCommon) > 0:
                if len(partnerInCommon) > 1:
                    print("find out what this case is, because I don't believe it's possible")
                partner = partnerInCommon[0]
                seen.append(partner)
                ancestorPairs.append(["full", person, data[person][0] + " & " + data[partner][0]])
            elif len(partnerInCommon) == 0:
                ancestorPairs.append(["half", person, data[person][0]])
        seen.append(person)
        
    for i in ancestorPairs:
        person = i[1]
        how = i[0] #full or half
        gen1 = whichGen(person, entry1) 
        gen2 = whichGen(person, entry2)
#         print(gen1, gen2)
        score = calculate(how, gen1, gen2)
        i.extend([score, [gen1, gen2]])
        
    ancestorPairs.sort(key = lambda x: x[-2])
    bestScore = ancestorPairs[0][-2]
    ancestorPairs = [i for i in ancestorPairs if i[-2] == bestScore]
    if bestScore == 4 and len(ancestorPairs) == 2:
        print(person1, "and", person2, "are double first cousins. This is a rare phenomenon;" )
        print("the two share 4/4 grandparents and are as closely related as half-siblings are.")
        #test with Johanna-Magdalene of Saxe-Weissenfels and Christiane-Wilhelmine of Saxe-Eisenach
         
    for i in ancestorPairs:
        person = i[1]
        gens = i[-1]
#         print(i[2]) #test with Albert-II MONACO and Victoria of Sweden to understand what i[2] is
        if i[0] == "full":
            if mode == 2:
                print("-----"*24)
                print(response.fullRelationship(gens, person1, person2, i[2], gender1, gender2) + ":")
                print()
                print(indirectFull(data, id1, id2, person, i[2], birthYear))
            else:
                print(response.fullRelationship(gens, person1, person2, i[2], gender1, gender2))
        elif i[0] == "half":
            if mode == 2:
                print("-----"*24) #separation for aesthetic purposes
                print(response.halfRelationship(gens, person1, person2, i[2], gender1, gender2) + ":")
                print()
                onepartner = set(entry1[gen1]) & set(partner_dic[person])
                twopartner = set(entry2[gen2]) & set(partner_dic[person])
                onepartner = list(onepartner)[0]
                twopartner = list(twopartner)[0]
                print(indirectHalf(onepartner, twopartner, data, id1, id2, person, birthYear))
            else:
                print(response.halfRelationship(gens, person1, person2, i[2], gender1, gender2))

    return ""

def getValidInput(choice, low, high):
    '''
    continually asks the user to try again if they input bad input
    '''
    while isStringInt(choice) == False:
        print("That was not one of the options. Try again.")
        choice = input("> ")
    choice = int(choice)
    while choice < low or choice > high:
        print("That was not one of the options. Try again.")
        choice = input("> ")
        while isStringInt(choice) == False:
            print("That was not one of the options. Try again.")
            choice = input("> ")
        choice = int(choice)
    return choice

def clean(data):
    '''
    some values in the csv have female fathers / male mothers, others assign phantom IDs to
    nonexistent people. This function does gender correction and removes IDs of people who dne
    data ia dictionary, returns cleaned dictionary
    '''
    men = childrenByG(data, "M")
    women = childrenByG(data, "F")
    for (k,v) in data.items():
        mother = v[6]
        motherName = v[7]
        if motherName == "":
            mother = ""
            v[6] = ""
        father = v[8]
        fatherName = v[9]
        if fatherName == "":
            father = ""
            v[9] = ""
        if father not in men and father != "" and father != '"':
#             print(k, father)
            v[6] = father
            v[7] = fatherName
        if mother not in women and mother != "" and mother != '"':
#             print(k, mother)
            v[8] = mother
            v[9] = motherName
#         if (mother, father).count("") == 1: #find individuals with only one known parent
#             print(v[0])
    return data
    #if last name has comma, replace with nothing
    
def siblings(data, id1, childNY):
    '''
    returns [full, maternal half, paternal half] siblings. list of sets.
    '''
    ret = [[id1]]
    buildPrevGen(data, ret) #test with Edmund Spencer (has all 3 types of siblings), Fernando of Spain
#         print(ret[-1])
    if ret[-1] == [0]: #no parents, so no siblings
        return [set(), set(), set()]
    if len(ret[-1]) == 1: #only one known parent, Denise von Hohenbuehel Genannt Heufler Zu Rasen is an example
        if data[ret[-1][0]][4] == "F":
            g = "maternal"
        else:
            g = "paternal"
        kinder = childNY[ret[-1][0]] #all children of the one parent
        kinder.remove(id1)
        if len(kinder) == 0: #no siblings
            return [set(), set(), set()]
        full = set()
        half = set()
        for person in kinder: #every person will have 1 or 2 parents. If 2, then must be half sibling.
            ls = [[person]]
            buildPrevGen(data, ls)
            if len(ls[-1]) == 2:
                half.add(person)
            else:
                full.add(person) #assume another sibling that only has one parent is full, could still be half
        if g == "maternal":
            return [full, half, set()]
        else:
            return [full, set(), half]
        
    if data[ret[-1][0]][4] == "M":
        dadSide = ret[-1][0]
        momSide = ret[-1][1]
    else:
        momSide = ret[-1][0]
        dadSide = ret[-1][1]
    momSide = childNY[momSide]
    dadSide = childNY[dadSide]
    momSide.remove(id1)
    dadSide.remove(id1)
    momSide = set(momSide)
    dadSide = set(dadSide)
    both = momSide&dadSide
    mom = momSide - dadSide 
    dad = dadSide - momSide
    return [both, mom, dad]

def noYear(data, ls):
    '''
    if individuals have unknown birth years, replace that unknown with either ??? or ????
    depending on whether the next individual (when sorted) with known birth year has 
    3 or 4 digit birth year
    '''
    withYears = [i for i in ls if i[1] != 0 and i[1] != ""]
    withoutYears = [i for i in ls if i[1] == 0 or i[1] == ""]
    if len(withYears) > 0:
        lenYears = len(str(withYears[0][1]))
        ls = [(i[0], "?"*lenYears) if i[1] == 0 or i[1] == "" else i for i in ls]
        return [i for i in ls if data[i[0]][0] != ""]
    if len(withoutYears) > 0: #only have people with unknown birth years
        ls = [(i[0], "????") if i[1] == 0 or i[1] == "" else i for i in ls]
    return [i for i in ls if data[i[0]][0] != ""]

def getYears(data):
    '''
    if year is unknown, let year be 0. This makes int sorting possible later
    '''
    d = {}
    for (k,v) in data.items():
        if v[13] == "":
            year = 0
        else:
            year = int(v[13])
        d[k] = year
    return d

def yearWithQ(data):
    '''
    if year is unknown, let year be ????
    so all years are strings. sorting works if no individual has birth year before 1000
    '''
    d = {}
    for (k,v) in data.items():
        if v[13] == "":
            year = "????"
        else:
            year = v[13]
        d[k] = year
    return d
    

def relational(file):
    '''
    mycket viktig! hur aer tvaa personer slaekt, om de verkligen aer slaekt?
    wie sind zwei Personen miteinander verwandt, wenn sie wirklich miteinander verwandt sind?
    '''
    global start_time
    dic = name_to_id(file)
    pick1 = pick_person(dic, "relation")
    id1 = pick1[0]
    ret = [[id1]]
    person1 = pick1[1]
    data = processFile(file)
    clean(data)
    gender1 = data[id1][4] 
    child = child_dic(data)
    childNY = child_noYear(data)
    genDict = patMatDict(data, gender1)
    years = getYears(data)

    print("What would you like to know?")
    print("0  for parents")
    print("1  for children")
    print("2  for siblings")
    print("3  for current and ex-partners")
    print("4  for grandparents")
    print("5  for grandchildren")
    print("6  for uncles")
    print("7  for aunts")
    print("8  for nieces")
    print("9  for nephews")
    print("10 for cousins")
    print("11 for descendants as list")
    print("12 for descendants by generation")
    print("13 for patrilineal/matrilineal descendants")
    print("14 for ancestors as list")
    print("15 for ancestors by generation")
    print("16 for matrilineal ancestors")
    print("17 for patrilineal ancestors")
    print("18 for ancestors who were monarchs")
    choice = input("> ")
    choice = getValidInput(choice, 0, 18)
    start_time = time.time()
    print(start_time)
    if choice == 0: #parents
        buildPrevGen(data, ret)
        for id in ret[-1]:
            print(data[id][0])
    elif choice == 1: #children
        ret = child[id1]
        if len(ret) == 0:
            print("no known children")
            return ""
        for id in ret:
            print(data[id[0]][0])
    elif choice == 2:
        (full, mom, dad) = siblings(data, id1, childNY)
#         print(full, mom, dad)
        if len(mom) == 0 and len(dad) == 0: #no half siblings
            if len(full) == 0:
                print("no siblings")
                return ""
            else:
                for sib in full:
                    print(data[sib][0])
                return ""
        if len(mom) != 0:
            print("maternal half siblings:")
            for sib in mom:
                print(data[sib][0])
            print ()
        if len(dad) != 0:
            print("paternal half siblings:")
            for sib in dad:
                print(data[sib][0]) 
            print()
        if len(full) != 0 and len(mom) == 0 and len(dad) == 0: #only has full siblings, no need to clarify full then
            for sib in full:
                print(data[sib][0])
        elif len(full) != 0:
            print("full siblings:")
            for sib in full:
                print(data[sib][0])
        return ""
    elif choice == 3: #current and ex partners
        current = data[id1][10]
        if current == "":
            print("no current partner")
        else:
            print(data[current][0])
        ex = data[id1][12].split()
        ex = [i for i in ex if i in data] #should be unnecessary, but weird IDs were being given for ex-partners for people who didn't have ex-partners
        if len(ex) == 1:
            if gender1 == "M":
                print("ex-wife is " + data[ex[0]][0])
            elif gender1 == "F":
                print("ex-husband is " + data[ex[0]][0])
            else:
                print("ex-partner is " + data[ex[0]][0])
        elif len(ex) > 1:
            if gender1 == "M":
                print("ex-wives below:")
            elif gender1 == "F":
                print("ex-husbands below:")
            else:
                print("ex-partners below:")
            for i in ex:
                print(data[i][0])
        return ""
    elif choice == 4: #grandparents
        gen = input("What generation? 0 for grandparents, 1 for great-grandparents, 2 for 2x great, and so on: > ")
        gen = getValidInput(gen, 0, 100)
        mode = input("Do you want 0 the grandparents listed individually by year or 1 listed as couples? > ")
        mode = getValidInput(mode, 0, 1)
        if mode == 0:
            for i in range(gen+2):
                buildPrevGen(data, ret)
            if ret[-1] == [0]:
                print("no recorded data of grandparents this far back")
                return ""
            grents = [(i, years[i]) for i in ret[-1]]
            grents.sort()
            grents.sort(key = operator.itemgetter(1))
            grents = noYear(data, grents)
            for id in grents:
                print(id[1], data[id[0]][0])
            return ""
        else:
            for i in range(gen+1):
                buildPrevGen(data, ret)
            if ret[-1] == [0]:
                print("no recorded data of grandparents this far back")
                return ""
            couples = []
            for preGrand in ret[-1]:
                temp = [[preGrand]]
                buildPrevGen(data, temp)
                rents = temp[-1]
                if rents != [0]:
                    couples.append(tuple(temp[-1]))
#             print(couples)
            if len(couples) == 0:
                print("no recorded data of grandparents this far back")
                return ""
            couples = list(set(couples))
            for cp in couples:
                one = data[cp[0]][0]
                if len(cp) == 1:
                    print(one + " and unknown")
                else:
                    two = data[cp[1]][0]
                    if one == "" and two != "":
                        print(two + " and unknown")
                    elif one != "" and two == "":
                        print(one + " and unknown")
                    elif one != "" and two != "":
                        print(data[cp[0]][0] + " and " + data[cp[1]][0])
            return ""
                
    elif choice == 5: #grandchildren
        gen = input("What generation? 0 for grandchildren, 1 for great-grandchildren, 2 for 2x great, and so on: > ")
        gen = getValidInput(gen, 0, 100)
        ret = [[(id1, data[id1][13])]]
        for i in range(gen+2):
            buildNextGen2(child, ret)
        if ret[-1] == [0]:
            print("no known " + str(gen) + "x grandchildren")
            return ""
        ret[-1] = list(set(ret[-1]))
        ret[-1].sort() #stable sort
        ret[-1].sort(key = operator.itemgetter(1))
        results = noYear(data, ret[-1])
        for id in results:
            name = data[id[0]][0]
            if name != "": #technically don't need this as noYear has been updated to remove people with no names
                print(id[1], data[id[0]][0])
    elif choice == 6 or choice == 7:
        if choice == 6:
            word = "uncle"
        else:
            word = "aunt"
        gen = input("What generation? 0 for " + word+ "s, 1 for great-" + word + "s, 2 for 2x great, and so on: >")
        gen = getValidInput(gen, 0, 100)      
        for i in range(gen+1):
            buildPrevGen(data, ret)
        if ret[-1] == [0]:
            print("no recorded data of " + str(gen) + "x " + word + "s this far back")
            return ""
        half = set()
        full = set()
        grents = ret[-1]
        for person in grents:
            (a, b, c) = siblings(data, person, childNY)
            half = half | b | c
            full = full | a
        half = {(i, years[i]) for i in half}
        full = {(i, years[i]) for i in full}
        fullUncles = {i for i in full if data[i[0]][4] == "M"}
        halfUncles = {i for i in half if data[i[0]][4] == "M"}
        fullAunts = full - fullUncles
        halfAunts = half - halfUncles
        fullUncles = sorted(fullUncles)
        fullUncles.sort(key = operator.itemgetter(1))
        halfUncles = sorted(halfUncles)
        halfUncles.sort(key = operator.itemgetter(1))
        fullAunts = sorted(fullAunts)
        fullAunts.sort(key = operator.itemgetter(1))
        halfAunts = sorted(halfAunts)
        halfAunts.sort(key = operator.itemgetter(1))
        
        fullUncles = noYear(data, fullUncles)
        halfUncles = noYear(data, halfUncles)
        fullAunts = noYear(data, fullAunts)
        halfAunts = noYear(data, halfAunts)
        
        if word == "uncle":
            if len(halfUncles) == 0 and len(fullUncles) == 0:
                print("no " + str(gen) + "x " + word + "s")
                return ""
            if len(halfUncles) == 0 and len(fullUncles) != 0:
                for id in fullUncles:
                    print(id[1], data[id[0]][0])
                return ""
            if len(halfUncles) > 0:
                print("half " + word + "s:")
                for id in halfUncles:
                    print(id[1], data[id[0]][0])
                print()
            if len(fullUncles) > 0:
                print("full " + word + "s:")
                for id in fullUncles:
                    print(id[1], data[id[0]][0])
            return ""
        else:
            if len(halfAunts) == 0 and len(fullAunts) == 0:
                print("no " + str(gen) + "x " + word + "s")
                return ""
            if len(halfAunts) == 0 and len(fullAunts) != 0:
                for id in fullAunts:
                    print(id[1], data[id[0]][0])
                return ""
            if len(halfAunts) > 0:
                print("half " + word + "s:")
                for id in halfAunts:
                    print(id[1], data[id[0]][0])
                print()
            if len(fullAunts) > 0:
                print("full " + word + "s:")
                for id in fullAunts:
                    print(id[1], data[id[0]][0])
    elif choice == 8 or choice == 9:
        if choice == 8:
            word = "niece"
        else:
            word = "nephew"
        gen = input("What generation? 0 for " + word+ "s, 1 for great-" + word + "s, 2 for 2x great, and so on: >")
        gen = getValidInput(gen, 0, 100)
        (full, mom, dad) = siblings(data, id1, childNY)
        if len(full) + len(mom) + len(dad) == 0:
            return "no known " + word + "s"
        half = list(mom | dad)
        full = list(full)
        halfNiblings = []
        fullNiblings = []
        for id in half:
            ret = [[id]]
            for j in range(gen+1):
                buildNextGen2(child, ret)
            if ret[-1] != [0]:
                halfNiblings += ret[-1]
#         print(full)
        for id in full:
            ret = [[(id, data[id][13])]] 
            for j in range(gen+1):
                buildNextGen2(child, ret)
            if ret[-1] != [0]:
                fullNiblings += ret[-1]
        halfNieces = [i for i in halfNiblings if data[i[0]][4] == "F"]
        halfNephews = [i for i in halfNiblings if data[i[0]][4] == "M"]
        fullNieces = [i for i in fullNiblings if data[i[0]][4] == "F"]
        fullNephews = [i for i in fullNiblings if data[i[0]][4] == "M"]
        halfNieces.sort()
        halfNieces.sort(key = operator.itemgetter(1))
        halfNephews.sort()
        halfNephews.sort(key = operator.itemgetter(1))
        fullNieces.sort()
        fullNieces.sort(key = operator.itemgetter(1))
        fullNephews.sort()
        fullNephews.sort(key = operator.itemgetter(1))
        if word == "niece":
            if len(halfNieces) + len(fullNieces) == 0:
                return "no known " + str(gen) + "x nieces"
            if len(halfNieces) == 0 and len(fullNieces) != 0: #no distinction necessary, all nieces are full
                for id in fullNieces:
                    print(id[1], data[id[0]][0])
                return ""
            if len(halfNieces) > 0:
                print("half " + str(gen) + "x nieces")
                for id in halfNieces:
                    print(id[1], data[id[0]][0])
                print()
            if len(fullNieces) > 0:
                print("full " + str(gen) + "x nieces")
                for id in fullNieces:
                    print(id[1], data[id[0]][0])
            return ""
        else:
            if len(halfNephews) + len(fullNephews) == 0:
                return "no known " + str(gen) + "x nephews"
            if len(halfNephews) == 0 and len(fullNephews) != 0: #no distinction necessary, all nephews are full
                for id in fullNephews:
                    print(id[1], data[id[0]][0])
                return ""
            if len(halfNephews) > 0:
                print("half " + str(gen) + "x nephews")
                for id in halfNephews:
                    print(id[1], data[id[0]][0])
                print()
            if len(fullNephews) > 0:
                print("full " + str(gen) + "x nephews")
                for id in fullNephews:
                    print(id[1], data[id[0]][0])
            return ""
        
    elif choice == 10:
        gen = input("Cousins in what way? For example, 4 2 means 4th cousin 2x removed, and 6 means 6th cousin: >")
        if len(gen.split()) == 1:
            gen = getValidInput(gen, 1, 100)
            a = gen
            b = 0
        else:
            a = int(gen.split()[0])
            b = int(gen.split()[1])
        #go up to one BEFORE common ancestor, then get half and full sibs
        ret = [[id1]]
        for i in range(a):
            buildPrevGen(data, ret)
        if ret[-1] == [0]:
            return "no known " + str(a) + " cousins " + str(b) + "x removed"
        full = []
        half = []
        for id in ret[-1]:
            both, mom, dad = siblings(data, id, childNY)
            full.extend(list(both))
            half.extend(list(mom | dad))
        fullCousins = []
        halfCousins = []
        for id in full:
            ret = [[(id, data[id][13])]] 
            for j in range(a+b):
                buildNextGen2(child, ret)
            if ret[-1] != [0]:
                fullCousins += ret[-1]
        for id in half:
            ret = [[(id, data[id][13])]] 
            for j in range(a+b):
                buildNextGen2(child, ret)
            if ret[-1] != [0]:
                halfCousins += ret[-1]  
                
        halfCousins = list(set(halfCousins))
        fullCousins = list(set(fullCousins))
        halfCousins.sort()
        halfCousins.sort(key = operator.itemgetter(1))
        fullCousins.sort()
        fullCousins.sort(key = operator.itemgetter(1))
        fullCousins = noYear(data, fullCousins) 
        halfCousins = noYear(data, halfCousins)
                  
        if len(halfCousins) + len(fullCousins) == 0:
            return "no known " + str(a) + " cousins " + str(b) + "x removed"
        if len(halfCousins) == 0 and len(fullCousins) != 0: #no distinction necessary, all cousins are full
            for id in fullCousins:
                if data[id[0]][0] != "" and data[id[0]][1] != "":
                    print(id[1], data[id[0]][0])
            return ""
        if len(halfCousins) > 0:
            print("half " + str(a) + " cousins " + str(b) + "x removed")
            for id in halfCousins:
                if data[id[0]][0] != "" and data[id[0]][1] != "":
                    print(id[1], data[id[0]][0])
            print()
        if len(fullCousins) > 0:
            print("full " + str(a) + " cousins " + str(b) + "x removed")
            for id in fullCousins:
                if data[id[0]][0] != "" and data[id[0]][1] != "":
                    print(id[1], data[id[0]][0])
        return ""        
            
        
    elif choice == 11: #descendants
        ret = [[(id1, data[id1][13])]]
        while ret[-1] != [0]:
            buildNextGen2(child, ret)
        if len(ret) == 2:
            print("no known descendants")
            return ""
        desc = collapse(ret[1:-1])
        desc = list(set(desc))
        desc.sort() #stable sort
        desc.sort(key = operator.itemgetter(1))
        desc = noYear(data, desc)
        for id in desc:
            print(id[1], data[id[0]][0])
        return ""
    elif choice == 12:#descendants by generation
        ret = [[(id1, data[id1][13])]]
        while ret[-1] != [0]:
            buildNextGen2(child, ret)
        if len(ret) == 2:
            print("no known " + " descendants")
            return ""
        desc = ret[1:-1]
        count = 1
        for generation in desc:
            generation.sort()
            generation.sort(key = operator.itemgetter(1))
            print("GENERATION " + str(count))
            generation = noYear(data, generation)
            for id in generation:
                name = data[id[0]][0]
                if name == "":
                    print("WHO IS THIS")
                else:
                    print(id[1], name)
            count += 1
            print()
        return ""
    elif choice == 13: #matrilineal / patrilineal descendants test with Gisela of Burgundy
        if gender1 == "M":
            word = "patrilineal"
        elif gender1 == "F":
            word = "matrilineal"
        else:
            return "" #can't do this one if gender is unknown
        ret = [[(id1, data[id1][13])]]
        while ret[-1] != [0]:
            buildNextGen2(genDict, ret)
        if len(ret) == 2:
            print("no known " + word + " descendants")
            return ""
        desc = ret[1:-1]
        count = 1
        for generation in desc:
            generation.sort()
            generation.sort(key = operator.itemgetter(1))
            print("GENERATION " + str(count))
            generation = noYear(data, generation)
            for id in generation:
                print(id[1], data[id[0]][0])
            count += 1
            print()
        return ""
    elif choice == 14 or choice == 15:
        ret = [[id1]]
        while ret[-1] != [0]:
            buildPrevGen(data, ret)
        ret = ret[1:-1]
        if len(ret) == 0:
            return ("not enough data for this person")
        if choice == 14:
            ancestors = list(set(collapse(ret)))
            ancestors = [i for i in ancestors if data[i][0] != "" and data[i][1] != ""]
            ancestors = [(i, years[i]) for i in ancestors]
            ancestors.sort()
            ancestors.sort(key = operator.itemgetter(1))
            ancestors = noYear(data, ancestors)
            for elem in ancestors:
                print(elem[1], data[elem[0]][0])
                
            return ""
        count = 1
        for gen in ret: #don't care about years here
            print("GENERATION " + str(count))
            for person in gen:
                name = data[person][0]
                if name != "":
                    print(name)
            print()
            count += 1
        return ""
    
    elif choice == 16 or choice == 17: #mother's mother's mother and father's father's father...
        ret = [[id1]]
        while ret[-1] != [0]:
            if choice == 16:
                oneGenderLine(data, ret, "F")
            else:
                oneGenderLine(data, ret, "M")
        ret = ret[1:-1]
        ret = collapse(ret)
        lastYear = 1111 #arbitrary four-digit int
        for person in ret:
            year = years[person]
            name = data[person][0]
            if name != "":
                if year == 0 or year == "":
                    print("?"*len(str(lastYear)), name)
                    lastYear = 1111
                else:
                    print(year, name)
                    lastYear = year
        return ""
        
    elif choice == 18: #ancestors who were monarchs
        while ret[-1] != [0]:
            buildPrevGen(data, ret)
        ret = ret[:-1]
        ret = list(set(collapse(ret)))
        ret.remove(id1)
        test = [(data[i][1], data[i][3], data[i][4]) for i in ret if data[i][1] == "Charlemagne" or ("the " in data[i][3] and len(data[i][3].split()) == 2 and data[i][3].split()[1] != "Junker")] #BUT avoid of the Palatinate, of the Netherlands, the Junker, of the Bourbon-Two-Sicilies, etc...
#         print(test) #test contains those rulers with nicknames
        lst = [(data[i][1], data[i][3], data[i][4]) for i in ret if data[i][3].isupper()]
        lst += test
        if len(lst) == 0:
            print("no known monarchs in ancestors")
            return ""
        lst.sort()
        lst.sort(key = operator.itemgetter(1))
        for item in lst:
            print(formatMonarch(item))
        return ""
    return ""

def cap(st):
    '''
    used for formatting monarchs. Given a string, i.e. "HOLY ROMAN EMPIRE", return a string where every first letter
    of original string is capitalized, all others lowered. -> "Holy Roman Empire"
    '''
    words = st.split()
    ret = []
    for w in words:
        ret.append(w[0].upper() + w[1:].lower())
    return " ".join(ret)

def formatMonarch(tup):
    '''
    formats monarchs. Most are in the form "regnalName - dash - regnalNumber - space - COUNTRY" i.e. "Christian-IX DENMARK"
    change kings to King <name> <regnal number> of <country>, queens to Queen <name> <regnal number> of <country>
    exceptions: 1) all Holy Roman Emperors are formatted as <name> <regnal number>, Holy Roman Emperor
                2) Mary, Queen of Scots was better known as such, so she is not default formatted into "Queen Mary of Scotland"
                3) all Dutch Kings and Queens have "the", as in "King/Queen of THE Netherlands" (cap for clarity)
                4) Charlemagne is formatted to be just plain ol' Charlemagne
                5) Rulers known by nicknames (i.e. Louis the Pious) are returned as such
    '''
    if "Charlemagne" in tup:
        return "Charlemagne"
    if tup == ('Mary', 'SCOTLAND', 'F'):
        return "Mary, Queen of Scots"
    if tup[1].isupper() == False: #one of the "x the y" rulers
        return tup[0] + " " + tup[1]
    first = tup[0].replace("-", " ")
    country = tup[1]
    if country == "HOLY ROMAN EMPIRE":
        last = ", Holy Roman Emperor"
        return first + last
    elif country == "NETHERLANDS":
        last = " of the Netherlands"
    elif len(country.split()) > 1:
        last = " of " + cap(country)
    else:
        last = " of " + country[0] + country[1:].lower()
    
    if tup[2] == "M":
        return "King " + first + last
    else:
        return "Queen " + first + last

def isStringInt(st):
    '''
    given a string, check if all its digits are ints
    '''
    nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    for char in st:
        if char not in nums:
            return False 
    return True

def ordinal(n):
    '''
    returns ordinal str version of int input, i.e. 1 -> first, 22 -> twenty second, etc. 
    '''
    return "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

def whichGen(id, entry):
    '''
    find out in which generation the ancestor appears, should definitely appear based on how entry was built, otherwise debug
    '''
    for i in range(len(entry)):
        if id in entry[i]:
            return i
    return "you need to debug"

def extract_years(dic, person):
    '''
    if one of the people chosen is a duplicate name,
    extract the years of all these people so the user
    can make it clear which person they mean
    k[:-2], so assuming there are at most 99 people with 
    the same name for any name, other zB Karl-Emich of Leiningen
    is a hit for Emich of Leiningen3 
    '''
    years = []
    short = {}
    i = 1
    for (k,v) in dic.items():
        if person in k and k[:-2] in person and isinstance(v, int) == False:
            if v[1] == "":
                v[1] = "unknown" + str(i)
                i += 1
            years.append(v[1])
            short[k] = v
#     print(print_lines(years))
    print((", ").join(sorted(years)))
    return short
    
def extract_person_given_year(short, year):
    '''
    once user supplies a year for those people who
    are duplicates, choose the specific person's ID
    '''
    for (k,v) in short.items():
        if v[1] == year:
            return v[0]
    return "no"

def collapse(lst):
    '''
    lst is a list of lists, returns elements of lst as one lst (not list of lists)
    '''
    ret = []
    for el in lst:
        for elem in el:
            ret.append(elem)
    return ret

def extract_similar(d, person): 
    '''
    if user types in a name that doesn't exist in the file, check if it's close to
    a name that does exist
    d is dictionary, person is string. 
    0.7 is arbitrary and can be adjusted. 
    '''
    person = person.lower()
    names = d.keys()
    if len(person.split()) == 1: #person is one word, either just first or last
        sim = []
        for name in names:
            namen = name.split() #list of length 2
            if len(namen) == 0:
                return "no sim"
            m = SequenceMatcher(None, person, namen[0].lower())
            if m.ratio() > 0.7:
                sim.append(name)
            else:
                m = SequenceMatcher(None, person, namen[-1].lower())
                if m.ratio() > 0.7:
                    sim.append(name)
        if len(sim) > 0:
            return sim
    sim = []
    for name in names:
        m = SequenceMatcher(None, person, name.lower())
        if m.ratio() > 0.7:
            sim.append(name)
    if len(sim) == 0:
        return "no sim"
    last = person.split()[-1]
    first = person.split()[0]
    sim2 = []
    for p in sim:
        if len(p.split()) == 1:
            sim2.append(p)
        elif p.split()[-1] == last:
            m = SequenceMatcher(None, first.lower(), p.split()[0].lower())
            if m.ratio() > 0.7:
                sim2.append(p)
    if len(sim2) > 0:
        return sim2
    return sim

def print_lines(lst): 
    '''
    takes a list and returns it line by line
    '''
    lst = sorted(lst)
    ret = ""
    for i in lst:
        ret += i + "\n"
    return ret.strip("\n")

if __name__ == '__main__':
    file = "England-28-Oct-2019-954.csv" 
#     file = "Prince-13-Nov-2019-275.csv"
    # file = "England-18-Nov-2019-424.csv"
#     file = "L-17-Nov-2019-908.csv"
    # file = "England-18-Sep-2019-913.csv"
    # file = "England-14-Oct-2019-800.csv"
    # file = "data.csv"
#     file = "Prince-13-Nov-2019-275.csv"
    file = "England-18-Nov-2019-424.csv"
#     file = "L-17-Nov-2019-908.csv"
    print("Which mode are you interested in?")
    choice = input("0 for how two people are related, 1 for relational information on a person, 2 for path of relation: > ")
    while choice != "0" and choice != "1" and choice != "2":
        choice = input("That was not one of the options. Try again: > ")
    if choice == "0":
        print(ask(file, 0))
    if choice == "1":
        print(relational(file))
    if choice == "2":
        print(ask(file, 2))
    
    print("It took ", time.time() - start_time, "seconds")
        
        
    
