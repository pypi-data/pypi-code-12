
import sys
import randomaya

def main():
    try:
        arg = sys.argv[1]
        randomaya.getTranslation(arg)

    except:
        print("<<>> Check your command, is it in the following format: \n randomaya <tag name>")


