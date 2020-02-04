'''
Created on Oct 31, 2019

@author: vlw12
'''
import copy
import algorithm
from datetime import datetime

def buildNextGen(data, ret):
    '''
    no longer in use because of existence of improved function. 
    ret begins as [[id]] and tacks on a new list of children each generation
    '''
    nextlst = []
    if ret[-1] == [0]:
        return ret
    nextlst = list(set([k for (k,v) in data.items() if (v[6] in ret[-1] or v[8] in ret[-1]) and v[1] != ""]))
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
        
def nextGenYears(data, ret):
    '''
    also no longer in use, having been replaced by buildNextGen2 (which in turns calls child_dic)
    '''
    nextlst = []
    if ret[-1] == [0]:
        return ret
    nextlst = list(set([(k, v[13]) for (k,v) in data.items() if (v[6] in func(ret[-1]) or v[8] in func(ret[-1])) and v[1] != ""]))
    if len(nextlst) > 0:
        ret.append(nextlst)
    else:
        ret.append([0])

def find(lst, id):
    '''
    lst is a list of lists. if id is in an innerlist of lst, return
    index of that innerlist, else return -1
    '''
    for i in range(len(lst)):
        for person in lst[i]:
            if person == id:
                return i
    return -1

def testcPG2(file):
    '''
    used to test the various incarnations of completePrevGen
    '''
    dic = algorithm.name_to_id(file)
    pick1 = algorithm.pick_person(dic, "one")
    pick2 = algorithm.pick_person(dic, "two")
    id1 = pick1[0]
    id2 = pick2[0]
    person1 = pick1[1]
    person2 = pick2[1]
    data = algorithm.processFile(file)
    algorithm.clean(data)       
    ret1 = [[id1]]
    ret2 = [[id1]]
    if not algorithm.isAncestor(data, id1, id2):
        return "person 2 needs to be older"
    while id2 not in ret1[-1]:
        completePrevGen2(data, ret1)
    while id2 not in ret2[-1]:
        algorithm.completePrevGen3(data, ret2, id2)
    print()
    print(ret1)
    print(ret2)
#     print(decode(ret2, data))
    return ""

def testPath(file):
    '''
    used to test the path() and path2() functions
    '''
#     id1 = "CXPEL" #william
#     id1 = "VS7A0" #queen
    id1 = "EOP1R" #leonor
#     id1 = "HT01V" #felipe vi
#     id2 = "WA8HD" #christian ix
    id2 = "NMU65" #gisela of burgundy
#     id2 = "M2GBN" #maria of austria 1531
#     id2 = "JVJFE" #victoria
#     id2 = "GLZIK" #george iii
    dic = algorithm.name_to_id(file)
    data = algorithm.processFile(file)
    algorithm.clean(data)
    
    tick = datetime.now()
    line = algorithm.path2(data, id1, id2)
    tock = datetime.now()
    print(tock-tick)
    
#     tick = datetime.now()
#     line = path(data, id1, id2)
#     tock = datetime.now()
#     print(tock-tick)
    
    print()
    if line == False:
        return "WRONG"
    print(len(line))
    for ls in line:
        for e in ls:
            print(data[e][0])
        print()
    return "DONE"

def decode(ls, data):
    '''
    ls is list of lists, used to make debugging easier
    '''
    ret = []
    for inner in ls:
        ret.append([i if i not in data else data[i][0] for i in inner])
#         ret.append([data[i][0] for i in inner])
    return ret

def completePrevGen2(data, ret):
    '''
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
            nextlst.append(mother) 
        elif mother == "":
            if len(nextlst) == 0:
                nextlst.append(1)
            elif isinstance(nextlst[-1], str):
                nextlst.append(1)
            else:
                nextlst[-1] += 1
        else:
            if len(nextlst) == 0:
                nextlst.append(mother)
            elif isinstance(nextlst[-1], str):
                nextlst.append(mother)
            else:
                nextlst[-1] += mother
        if isinstance(father, str) and father != "":
            nextlst.append(father) 
        elif father == "":
            if len(nextlst) == 0:
                nextlst.append(1)
            elif isinstance(nextlst[-1], str):
                nextlst.append(1)
            else:
                nextlst[-1] += 1
        else:
            if len(nextlst) == 0:
                nextlst.append(father)
            elif isinstance(nextlst[-1], str):
                nextlst.append(father)
            else:
                nextlst[-1] += father
    ret.append(nextlst)
    return ret

def completePrevGen(data, ret):
    '''
    used only in path search. doesn't remove duplicates. generations should be perfectly exponential by factor of 2
    sad, this causes memory error when finding path between two people many generations apart
    '''
    nextlst = [] 
    for id in ret[-1]:
        if id == "":
            mother = ""
            father = ""
        else:
            mother = data[id][6]
            father = data[id][8]
        nextlst.append(mother) 
        nextlst.append(father)
    ret.append(nextlst)
    return ret

def path(data, id1, id2):
    '''
    id1 is YOUNGER, id2 is OLDER
    returns the shortest path(s) from id1 up to id2
    '''
    if not algorithm.isAncestor(data, id1, id2):
        return False #mistake has been made, id2 is NOT ancestor of id1
    paths = [[id1]]
    ret = [[id1]]
    while id2 not in ret[-1]:
        completePrevGen(data, ret)
    ret = ret[1:]
#     print(ret)
    momWas = False
    for gen in range(len(ret)):
        for individual in range(len(ret[gen])):
            person = ret[gen][individual]
            if algorithm.isAncestor(data, person, id2): #if id2 is an ancestor of person
                ind = 0
                if gen == 0 and individual == 0:
                    ind = 0
                    momWas = True
                elif gen == 0 and individual == 1 and momWas:
                    ind = -1
                elif gen != 0:
                    ind = algorithm.getIdx(paths, ret[gen-1][individual//2])
                if ind == -1:
                    ind = algorithm.getIdxPrev(paths, ret[gen-1][individual//2])
                    root = paths[ind][:-1]
                    paths.append(root + [(person, "fresh")])
                else:
                    root = paths[ind]
                    root += [(person, "fresh")]
                    
        for entries in paths:
            entries[-1] = entries[-1][0] #remove the fresh, no longer fresh
#         debug = decode(paths, data)
#         for x in debug:
#             print(x)
#         print()
    #len(paths) is exactly how many ways id1 is descended from id2
    paths = [i for i in paths if i[-1] == id2]
    return paths

def create_entry(data, person):
    '''
    data is a result of a call to processFile()
    no longer in use, with creation of buildPrevGen()
    '''
    done = False
#     partner_data = get_partners(data)
#     partners = partner_data[person]
    ret = []
    selber = [person] #+ partners
    ret.append(selber)
    while done == False:
        nextlst = []
        for id in selber:
            if selber.count("") == len(selber):
                done = True
            if id != "":
                nextlst.append(data[id][6]) #mother
                nextlst.append(data[id][8]) #father
        if done == False:
            ret.append([i for i in nextlst if i != ""])
        selber = copy.deepcopy(nextlst)
    return ret

def patMatDict2(data):
    '''
    keep all daughters of women, keep all sons of men
    '''
    male = {}
    female = {}
    for (k,v) in data.items():
        mother = v[6] 
        father = v[8]
        gender = v[4]
        if gender == "F":
            if mother != "":
                if mother not in female:
                    female[mother] = [(k, v[13])]
                else:
                    female[mother].append((k, v[13]))
        elif gender == "M":
            if father != "":
                if father not in male:
                    male[father] = [(k, v[13])]
                else:
                    male[father].append((k, v[13]))
    return male, female

if __name__ == '__main__':
    pass
