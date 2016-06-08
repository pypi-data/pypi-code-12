threshold = 0.4
thresholdAbsolute = 20
caseSensitive = False
nullResultValue = None
returnWinningObject = None
returnFirstMatch = False

def didYouMean(txt, match, key=None):
    if txt == None:
        return None

    if not caseSensitive:
        txt = txt.lower()

    thresholdRelative = threshold == None and None or threshold * len(txt)
    winningVal = None

    if thresholdRelative != None and thresholdAbsolute != None:
        winningVal = min(thresholdRelative, thresholdAbsolute)
    elif thresholdRelative != None:
        winningVal = thresholdRelative;
    elif thresholdAbsolute != None:
        winningVal = thresholdAbsolute
    else:
        winning = None

    winner = None

    for i, candidate in enumerate(match):
        if key != None:
            candidate = candidate[key]

        if candidate == None:
            continue

        testCandidate = caseSensitive and lower(candidate) or candidate
        val = getEditDistance(txt, testCandidate, winningVal)

        if winningVal == None or val < winningVal:
            winningVal = val

            winner = (key and returnWinningObject) and match[i] or candidate

            if returnFirstMatch:
                return winner

    return winner or nullResultValue

def charAt(txt, i):
    ret = ""

    try:
        ret = txt[i]
    except:
        pass

    return ret

MAX_INT = pow(2, 32) - 1

def getEditDistance(a, b, m):
    m = m or (max == 0 and max or MAX_INT)

    lena, lenb = len(a), len(b)

    if lena == 0:
        return min(m + 1, lenb)

    if lenb == 0:
        return min(m + 1, lena)

    if abs(lena - lenb) > m:
        return m + 1

    matrix = []

    for i in range(0, lenb + 1):
        matrix.append([i])

    for j in range(0, lena + 1):
        matrix[0].append(j)

    for i in range(1, lenb + 1):
        colMin = MAX_INT
        minJ = 1

        if i > m:
            minJ = i - m

        maxJ = lenb + 1

        if maxJ > m + i:
            maxJ = m + i

        for j in range(1, lena + 1):
            if j < minJ or j > maxJ:
                try:
                    matrix[i][j] = m + 1
                except:
                    matrix[i].append(m + 1)
            else:
                if charAt(b, i - 1) == charAt(a, j - 1):
                    try:
                        matrix[i][j] = matrix[i - 1][j - 1]
                    except:
                        matrix[i].append(matrix[i - 1][j - 1])
                else:
                    setTo = min(matrix[i - 1][j - 1] + 1,
                                min(matrix[i][j - 1] + 1,
                                matrix[i - 1][j] + 1))
                    try:
                        matrix[i][j] = setTo
                    except:
                        matrix[i].append(setTo)


            if matrix[i][j] < colMin:
                colMin = matrix[i][j]

        if colMin > m:
            return m + 1

    return matrix[lenb][lena]
