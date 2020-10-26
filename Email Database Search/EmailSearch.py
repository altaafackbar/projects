import string, re, operator
from bsddb3 import db

outputMode = "brief"
validInput = True # to prevent runing search on invlaid input
ops = { ">": operator.gt, "<": operator.lt,":": operator.eq, 'in':operator.contains, ">=": operator.ge, "<=": operator.le} # etc.


def reformatSpaces(query):
    # replace multiple spaces with just one
    query = query.split()
    query = " ".join(query)

    # remove spaces between :,<,> and terms
    ops = [":", "<", ">","="]
    rebuiltString = ""
    for i in range(0, len(query)):
        if query[i] != " ":
            rebuiltString += query[i]
        elif query[i] == " " and query[i-1] not in ops and query[i+1] not in ops:
            rebuiltString += query[i]

    return rebuiltString

def checkCondition(col, operator, condition):
    colNames = ["subj", "body", "term", "to", "from", "email", "bcc", "cc", "date"]
    termValidChars = string.ascii_lowercase + string.digits + "-_"
    emailSpecial = ".@"

    out = {}
    out["col"] = col
    out["operator"] = operator

    if col in colNames[0:8] and operator != ":":
        print("Condition {0}{1}{2} is of incorrect form.\n{0} cannot be used with {1}".format(col, operator, condition))
        return None

    # term format
    if col in colNames[0:3]:
        out["partial"] = False
        
        exp = r"(\w|-)+%*"
        match = re.match(exp, condition)
        
        if not match or (match and not match.span() == (0, len(condition))):
            print("Malformed term")
            return None

        if condition[-1] == "%":
            out["partial"] = True

    # email format
    elif col in colNames[3:8]:

        exp = r"((\w|-)+\.)*(\w|-)+@((\w|-)+\.)*(\w|-)+"
        match = re.match(exp, condition)
        #print(match)
        if not match or (match and not match.span() == (0, len(condition))):
            print("Malformed Email")
            return None

    
    # date format
    elif col == "date":
        exp = r"\d{4}/\d{2}/\d{2}"
        match = re.match(exp, condition)
        if not match or (match and not match.span() == (0, 10)):
            print("Malformed date. Must in in format YYYY/MM/DD")
            return None

    
    out["condition"] = condition
    return out


def parseQuery(query):
    global validInput
    global outputMode
    validInput = True
    # The only remaining spaces are between conditions
    query = reformatSpaces(query)
    qChunks = query.split()
    
    parameters = []
    for chunk in qChunks:
        if chunk == "output=full":
            outputMode = "full"
            validInput = False
            continue
        elif chunk == "output=brief":
            outputMode = "brief"
            validInput = False
            continue

        col = ""
        condition = ""
        operator = ""
        if ":" in chunk:
            i = chunk.find(":")
            col = chunk[:i]
            condition = chunk[i+1:]
            operator = ":"
        elif "<" in chunk:
            i = chunk.find("<")
            col = chunk[:i]
            if chunk[i+1] == "=":
                condition = chunk[i+2:]
                operator = "<="
            else:
                condition = chunk[i+1:]
                operator = "<"
        elif ">" in chunk:
            i = chunk.find(">")
            col = chunk[:i]
            if chunk[i+1] == "=":
                condition = chunk[i+2:]
                operator = ">="
            else:
                condition = chunk[i+1:]
                operator = ">"
        else:
            col = "term"
            operator = ":"
            condition = chunk

        split = checkCondition(col, operator, condition)
        if split is not None:
            parameters.append(split)
        else:
            print("Ignoring condition:",chunk)
            validInput = False
    return parameters



def queryR(conditions):
    inter = []
    terms = []
    for i in conditions:
        print(i)
        col = i['col']
        op = i['operator']
        con = i['condition']
        

        if col == 'date':
            matches = [] 
            dtb = db.DB()
            dtb.open('da.idx',None, db.DB_BTREE, db.DB_CREATE)
            curs = dtb.cursor()
            itr = curs.first()
            while itr:
                key = str(itr[0].decode("utf-8"))
                data = str(itr[1].decode("utf-8"))
                
                if ops[op](key,con):
                    matches.append(int(data))
                itr = curs.next()
            curs.close()
            dtb.close() 
            inter.append(matches)
            
        elif col in ["bcc", "cc", "from", "to"]:
            matches = []
            dtb = db.DB()
            dtb.open('em.idx',None, db.DB_BTREE, db.DB_CREATE)
            curs = dtb.cursor()
            itr = curs.first()
            while itr:
                key = str(itr[0].decode("utf-8"))
                data = str(itr[1].decode("utf-8"))
                quer = str(col+'-'+con)
                if ops[op](quer,key):
                    matches.append(int(data))
                itr = curs.next()
            curs.close()
            dtb.close()
            inter.append(matches)

        elif col in ["term", "subj", "body"]:
            terms.append(i)

    if len(terms) > 0:
        inter.append(dbFindFast(terms))
    try:
        setAll = set.intersection(*map(set,inter))
    except:
        setAll = None
    if setAll == None:
        return 'No matches'
    return setAll

def dbFindAllTerms(terms):
    allmatches = []
    dtb = db.DB()
    dtb.open('te.idx',None, db.DB_BTREE, db.DB_CREATE)
    curs = dtb.cursor()
    itr = curs.first()

    while itr:
        key = str(itr[0].decode("utf-8"))
        data = str(itr[1].decode("utf-8"))

        location = key[0]
        key = key[2:]

        for term in terms:
            col = term["col"]
            partial = term["partial"]
            cond = term["condition"]
            
            if (not partial and cond == key) or (partial and cond[:-1] == key[:len(cond[:-1])]):
                if (col != "term" and col[0] == location) or col == "term":
                    if "matches" not in term:
                        term["matches"] = []
                    
                    term["matches"].append(int(data))
        itr = curs.next()
    curs.close()
    dtb.close()

    for term in terms:
        if "matches" in term:
            allmatches.append(term["matches"])
        else:
            allmatches.append([])
    allmatches = set.intersection(*map(set,allmatches))
    return allmatches

def dbFindFast(terms):
    allmatches = []
    dtb = db.DB()
    dtb.open('te.idx',None, db.DB_BTREE, db.DB_CREATE)
    curs = dtb.cursor()
    
    for term in terms:
        col = term["col"]
        partial = term["partial"]
        cond = term["condition"]
        term["matches"] = []
        
        if partial:
            cond = cond[:-1]

        search = "{}-{}".format(col[0],cond)
        if col == "term":
            search = "b" + search[1:]

        itr = curs.set_range(search.encode("utf-8"))
        
        
        while True:
            if itr is None and col != "term":
                break
            elif itr is None and col == "term" and search[0] == "s":
                break
            elif itr is None and col == "term" and search[0] == "b":
                search = "s" + search[1:]
                itr = curs.set_range(search.encode("utf-8"))
                continue
 
            key = str(itr[0].decode("utf-8"))
            data = str(itr[1].decode("utf-8"))

            if partial:
                print(search[2:],key[2:len(search)])

            if (not partial and search[2:] == key[2:]) or (partial and search[2:] == key[2:len(search)]):
                if col != "term" and col[0] == key[0]:
                    term["matches"].append(int(data))                
                elif col == "term":
                    term["matches"].append(int(data))
            else:
                if col == "term" and search[0] == "b":
                    search = "s" + search[1:]
                    itr = curs.set_range(search.encode("utf-8"))
                    continue
                else:
                    break
            itr = curs.next()
        
    curs.close()
    dtb.close()

    for term in terms:
        if "matches" in term:
            allmatches.append(term["matches"])
            print(term["matches"])
        else:
            allmatches.append([])
    allmatches = set.intersection(*map(set,allmatches))
    return allmatches

def dbResult(index):
    dtb = db.DB()
    dtb.open('re.idx',None, db.DB_HASH, db.DB_CREATE)
    curs = dtb.cursor()
    print(outputMode)
    if outputMode == "brief":
        # for each result
        for i in index:   
            i = str(i)
            # goes to result
            itr = curs.set(i.encode("utf-8"))
            raw = itr[1].decode("utf-8")
            # only keeps subject and row
            subject = re.search('<subj>(.*)</subj>', raw)
            row = re.search('<row>(.*)</row>', raw)
            if subject != None:
                subject = subject.group(1)
            if row != None:
                row = row.group(1)
            print("Row: " + row + " | Subject: " + subject)
    elif outputMode == "full":
        for i in index:   
            i = str(i)
            # goes to result
            itr = curs.set(i.encode("utf-8"))
            raw = itr[1].decode("utf-8")
            # breaks it up
            data = ['']*8
            data[0] = re.search('<row>(.*)</row>', raw)
            data[1] = re.search('<date>(.*)</date>', raw)
            data[2] = re.search('<from>(.*)</from>', raw)
            data[3] = re.search('<to>(.*)</to>', raw)
            data[4] = re.search('<subj>(.*)</subj>', raw)
            data[5] = re.search('<cc>(.*)</cc>', raw)
            data[6] = re.search('<bcc>(.*)</bcc>', raw)
            data[7] = re.search('<body>(.*)</body>', raw)
            for j in range(len(data)):
                if data[j] != None:
                    data[j] = data[j].group(1)
            print("Row: "+ data[0] + "================================================")
            print("Date: "+ data[1])
            print("From: "+ data[2])
            print("To: "+ data[3])
            print("Subject: "+ data[4])
            print("CC: "+ data[5])
            print("BCC: "+ data[6])
            print("Body: "+ data[7])
    curs.close()
    dtb.close()

if __name__ == "__main__":
    while True:
        print("\n\nPlease enter a query")
        query = input(">").lower()
        conditions = parseQuery(query)
        if validInput:
            results = queryR(conditions)
            dbResult(results)
