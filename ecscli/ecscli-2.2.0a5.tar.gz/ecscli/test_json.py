import sys
import json




#http://kaira.sgo.fi/2014/05/saving-and-loading-data-in-python-with.html
def saveVar(data, varName):
    varFilename = varName + "test_json_sample_" + varName + ".json"
    out_file = open(varFilename,"w")
    json.dump(data,out_file, indent=4)
    out_file.close()

def loadVar(fileName):
    print("loading " + fileName)
    in_file = open(fileName,"r")
    result = json.load(in_file)
    in_file.close()
    print(str(result))
    return result


result1 = loadVar(sys.argv[1])
result2 = loadVar(sys.argv[2])
finalResult = []
finalResult.append(result1)
finalResult.append(result2)
saveVar(finalResult, "user_mapping")
