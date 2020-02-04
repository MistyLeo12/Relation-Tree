'''
Created on Oct 31, 2019

@author: vlw12
'''
import math

def response1(num, person1, person2, gender2):
    '''
    person2 is from an older generation than person1
    '''
    if num == 2:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s grandfather"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s grandmother"
        return person2 + " is " + person1 + "'s grandparent"
    if num == 1:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s father"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s mother"
        return person2 + " is " + person1 + "'s parent"
    if num == 3:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s great-grandfather"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s great-grandmother"
        return person2 + " is " + person1 + "'s great-grandparent"
    if num < 50:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s " + str(num-2) + "x great-grandfather"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s " + str(num-2) + "x great-grandmother"
        return person2 + " is " + person1 + "'s " + str(num-2) + "x great-grandparent"
    return "you need to debug"

def response2(num, person1, person2, gender2):
    '''
    person2 is from a younger generation than person1
    '''
    if num == 2:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s grandson"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s granddaughter"
        return person2 + " is " + person1 + "'s grandchild"
    if num == 1:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s son"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s daughter"
        return person2 + " is " + person1 + "'s child"
    if num == 3:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s great-grandson"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s great-granddaughter"
        return person2 + " is " + person1 + "'s great-grandchild"
    if num < 50:
        if gender2 == "M":
            return person2 + " is " + person1 + "'s " + str(num-2) + "x great-grandson"
        if gender2 == "F":
            return person2 + " is " + person1 + "'s " + str(num-2) + "x great-granddaughter"
        return person2 + " is " + person1 + "'s " + str(num-2) + "x great-grandchild"
    
def ordinal(n):
    return "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
    
def fullRelationship(gens, person1, person2, ancestor, gender1, gender2):
    gen1 = gens[0] 
    gen2 = gens[1]
    if gens.count(1) == 2: 
        if gender1 == "M":
            if gender2 == "M":
                return (person1 + " and " + person2 + " are brothers")
            if gender2 == "F":
                return (person1 + " and " + person2 + " are brother and sister")
            return (person1 + " is " + person2 + "'s brother")
        if gender1 == "F":
            if gender2 == "M":
                return (person1 + " and " + person2 + " are sister and brother")
            if gender2 == "F":
                return (person1 + " and " + person2 + " are sisters")
            return (person1 + " is " + person2 + "'s sister")
        return (person1 + " and " + person2 + " are siblings")
    elif gens.count(1) == 1 and gens.count(2) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s aunt")
            return (person1 + " is " + person2 + "'s aunt/uncle")
        else:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s nephew")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s niece")
            return (person1 + " is " + person2 + "'s niece/nephew")
    elif gens.count(1) == 1 and gens.count(3) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s grand uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s grand aunt")
            return (person1 + " is " + person2 + "'s grand aunt/uncle")
        else:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s grand nephew")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s grand niece")
            return (person1 + " is " + person2 + "'s grand niece/nephew")
    elif gens.count(1) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s " + str(gen2-gen1-1) +"x great grand uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s " + str(gen2-gen1-1) +"x great grand aunt")
            return (person1 + " is " + person2 + "'s " + str(gen2-gen1-1) +"x great grand aunt/uncle")
        else:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s " + str(gen1-gen2-1) +"x great grand nephew")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s " + str(gen1-gen2-1) +"x great grand niece")
            return (person1 + " is " + person2 + "'s " + str(gen1-gen2-1) +"x great grand niece/nephew")
    elif gen1==gen2:
        return (person1 + " and " + person2 + " are " + ordinal(gen1-1) + " cousins through " + ancestor)
    return (person1 + " and " + person2 + " are " + ordinal(min(gen1, gen2)-1) + " cousins " + str(abs(gen1-gen2)) + "x removed through " + ancestor)

    
def halfRelationship(gens, person1, person2, ancestor, gender1, gender2):
    gen1 = gens[0] 
    gen2 = gens[1]
    if gens.count(1) == 2: #half siblings
        if gender1 == "M":
            if gender2 == "M":
                return (person1 + " and " + person2 + " are half-brothers")
            return (person1 + " is " + person2 + "'s half-brother") #brother and sister or brother and gender unknown
        if gender1 == "F":
            if gender2 == "F":
                return (person1 + " are " + person2 + " are half-sisters")
            return (person1 + " is " + person2 + "'s half-sister")
        return (person1 + " and " + person2 + " are half-siblings")
    elif gens.count(1) == 1 and gens.count(2) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s half uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s half aunt")
            return (person1 + " is " + person2 + "'s half aunt/uncle")
        else:
            if gender1 == "M":
                return ((person1 + " is " + person2 + "'s half nephew"))
            if gender1 == "F":
                return ((person1 + " is " + person2 + "'s half niece"))
            return ((person1 + " is " + person2 + "'s half niece/nephew"))
    elif gens.count(1) == 1 and gens.count(3) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s half grand uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s half grand aunt")
            return (person1 + " is " + person2 + "'s half grand aunt/uncle")
        else:
            if gender1 == "M":
                return ((person1 + " is " + person2 + "'s half grand nephew"))
            if gender1 == "F":
                return ((person1 + " is " + person2 + "'s half grand niece"))
            return ((person1 + " is " + person2 + "'s half grand niece/nephew"))
    elif gens.count(1) == 1:
        if gen1 == 1:
            if gender1 == "M":
                return (person1 + " is " + person2 + "'s half " + str(gen2-gen1-1) +"x great grand uncle")
            if gender1 == "F":
                return (person1 + " is " + person2 + "'s half " + str(gen2-gen1-1) +"x great grand aunt")
            return (person1 + " is " + person2 + "'s half " + str(gen2-gen1-1) +"x great grand aunt/uncle")
        else:
            if gender1 == "M":
                return ((person1 + " is " + person2 + "'s half " + str(gen1-gen2-1) +"x great grand niece"))
            if gender1 == "F":
                return ((person1 + " is " + person2 + "'s half " + str(gen1-gen2-1) +"x great grand niece"))
            return ((person1 + " is " + person2 + "'s half " + str(gen1-gen2-1) +"x great grand niece/nephew"))
    elif gen1==gen2:
        return (person1 + " and " + person2 + " are half " + ordinal(gen1-1) + " cousins through " + ancestor)
    return (person1 + " and " + person2 + " are half " + ordinal(min(gen1, gen2)-1) + " cousins " + str(abs(gen1-gen2)) + "x removed through " + ancestor)


if __name__ == '__main__':
    pass
