from collections import defaultdict # used for finding unallowed moves in pythonic way
from pyeda.inter import * # used for BDD

""" Using for coloring the console. """
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


""" Class for the board
Defines the data layer.
Creates board as a n*n list
Containts functions to take input for the board and print the board
"""
class nQueens:
  def __init__(self, n, hints = 1, header = 1):
    self.nArr = [[0 for x in range(n)] for x in range(n)]
    print(color.GREEN+"Board initiated."+color.END)
    self.hints = hints
    print(color.BOLD+color.BLUE+"Hints kept "+{0:"off", 1:"on"}[hints]+color.END+". Type hints=0 or hints=1 to turn off or on hints")
    self.header = header
    print(color.BOLD+color.BLUE+"Header kept "+{0:"off", 1:"on"}[header]+color.END+". Type header=0 or header=1 to turn off or on header")

  def printInline(self):
    print(self.nArr)
  
  def putQueen(self, i, j):
    self.nArr[i][j] = 1
  
  def removeQueen(self, i, j):
    self.nArr[i][j] = 0
  
  def disallowQueens(self, listOfTuples):
    for i in listOfTuples:
      self.nArr[i[0]][i[1]] = -1
  
  # use board array to find spot left
  def spotLeft(self, n):
    for i in range(n):
      for j in range(n):
        if self.nArr[i][j]==0:
          return True
    return False

  def pprint(self):
    if self.header == 1:
      # print top header
      print(color.BOLD+color.BLUE+" \  " + ''.join(['{:4}'.format(item) for item in range(len(self.nArr[0]))])+color.END)
      # print seperator
      print(color.BOLD+color.BLUE+"  | " + ''.join(['{:4}'.format(item) for item in ['----']*len(self.nArr[0])])+color.END)
      if self.hints == 1:
        # print left header + seperator + rows (coloured and with hints)
        print('\n'.join([(color.BOLD+color.BLUE+str(idx)+" | " + color.END+ ''.join(['{:4}'.format(item) if item==0 else color.RED+'{:4}'.format(item)+color.END if item==-1 else color.GREEN+'{:4}'.format(item)+color.END for item in self.nArr[idx]])) for idx in range(len(self.nArr))]))
      else:  
        # print left header + seperator + rows
        print('\n'.join([(color.BOLD+color.BLUE+str(idx)+" | " + color.END+ ''.join(['{:4}'.format(item) if item>=0 else '{:4}'.format(0) for item in self.nArr[idx]])) for idx in range(len(self.nArr))]))
      print('\n')
    else:
      # print 2d array without headers
      if self.hints == 1:
        # print rows (coloured and with hints)
        print('\n'.join([(''.join(['{:4}'.format(item) if item==0 else color.RED+'{:4}'.format(item)+color.END if item==-1 else color.GREEN+'{:4}'.format(item)+color.END for item in self.nArr[idx]])) for idx in range(len(self.nArr))]))
      else:  
        # print left header + seperator + rows
        print('\n'.join([(''.join(['{:4}'.format(item) if item>=0 else '{:4}'.format(0) for item in self.nArr[idx]])) for idx in range(len(self.nArr))]))
      print('\n')

  def askInput(self, n, msg="Enter row and col: "):
    input_msg = input(msg)
    # help message
    if (input_msg.lower())=="help":
      print("\nThis is a proof of concept for using binary decision diagram for solving n Queen problem. Boards of size greater than 3 can be initiated. Once the board is initated, you are asked to place number of queens(which is equal to board size) one by one - specifying row and column number, seperated by space. The board is printed before each move with 0 representing squares that are empty and playable, 1 represents square occupied by queens and -1 represent square that are empty but placing queens aren't allowed on such squares as violate the condition of n Queen problem. At time of each input, one may either play or type one of the following commands: ")
      print(color.BOLD+"help"+color.END+": to read this text (again)")
      print(color.BOLD+"hints=0"+color.END+": to turn off the hints (-1 will not be shown)")
      print(color.BOLD+"hints=1"+color.END+": to turn on the hints (-1 will be shown)")
      print(color.BOLD+"header=0"+color.END+": to turn off the header (remember the row and column count is 0 initialised)")
      print(color.BOLD+"header=1"+color.END+": to turn on the header")
      print(color.BOLD+"auto"+color.END+": to play one move on your behalf")
      print("\n")
      return self.askInput(n, msg=msg)
    # auto play
    elif (input_msg.lower()[:4])=="auto":
      for row_n_auto in range(n):
        for col_n_auto in range(n):
          if self.nArr[row_n_auto][col_n_auto]==0:
            print("Playing automatically on " +color.BOLD+color.BLUE+ str(row_n_auto) + ", " + str(col_n_auto) + color.END)
            return row_n_auto, col_n_auto
      print(color.BOLD+color.RED+"Unable to find. You try. "+color.END)
      return self.askInput(n, msg=msg)
    # hint toggle
    elif (input_msg[:4].lower())=="hint":
      self.hints = int(input_msg[-1])
      print("Hints kept "+{0:"off", 1:"on"}[self.hints]+". Type hints=0 or hints=1 to turn off or on hints")
      self.pprint()
      return self.askInput(n, msg=msg)
    # header toggle
    elif (input_msg[:6].lower())=="header":
      self.header = int(input_msg[-1])
      print("Header kept "+{0:"off", 1:"on"}[self.header]+". Type header=0 or header=1 to turn off or on header")
      self.pprint()
      return self.askInput(n, msg=msg)
    # move play
    else:
      try:
        i, j = map(int, input_msg.split())
      except:
        # not convertible to int
        print(color.BOLD+color.RED+"Unacceptable row and col recieved"+color.END)
        return self.askInput(n, msg=msg)
      if (i >= n or j >= n or self.nArr[i][j]!=0):
        # not in the board or occupied or illegal
        print(color.BOLD+color.RED+"Unacceptable row and col recieved"+color.END)
        return self.askInput(n, msg=msg)
      else:
        return i, j


"""class for BDD
Defines the logic layer : not complete logic layer
(Some logic in the nQueensSolver)
The logic layers are seperated so as to keep the BDD calls in completely seperate class.
Class initialises with the constraint expression for the n Queens problem
Contains functions to restrict the solution(putQueen), list all solution(findUnallowedMoves)
"""
class nQueensBDD:
  def __init__(self, n = 8):
    # defining n*n variables
    X = exprvars('x', n, n)

    # defining row and column constraint
    rowConstraint = And(*[OneHot(*[X[r,c] for c in range(n)]) for r in range(n)])
    colConstraint = And(*[OneHot(*[X[r,c] for r in range(n)]) for c in range(n)])
    
    # TODO - rephrase
    # defining diagonal left to right constraint
    starts = [(i, 0) for i in range(n-2, 0, -1)] + [(0, i) for i in range(n-1)]
    lrdiags = []
    for r, c in starts:
        lrdiags.append([])
        ri, ci = r, c
        while ri < n and ci < n:
            lrdiags[-1].append((ri, ci))
            ri += 1
            ci += 1
    diagonalLeft2RightConstraint = And(*[OneHot0(*[X[r,c] for r, c in diag]) for diag in lrdiags])
    
    # TODO - rephrase
    # defining diagonal right to left constraint
    starts = [(i, n-1) for i in range(n-2, -1, -1)] + [(0, i) for i in range(n-2, 0, -1)]
    rldiags = []
    for r, c in starts:
        rldiags.append([])
        ri, ci = r, c
        while ri < n and ci >= 0:
            rldiags[-1].append((ri, ci))
            ri += 1
            ci -= 1
    diagonalRight2LeftConstraint = And(*[OneHot0(*[X[r,c] for r, c in diag]) for diag in rldiags])
    
    print(color.GREEN+"BDD vairables initiated."+color.END)
    # Add constraints to a single expression
    self.constraintExpr = rowConstraint & colConstraint & diagonalLeft2RightConstraint & diagonalRight2LeftConstraint
    print(color.GREEN+"BDD constaint expression initiated."+color.END)
    # keeping defined exprvariable for future use
    self.bddVariables = X
  
  def putQueen(self, i, j):
    self.constraintExpr = self.constraintExpr.restrict({self.bddVariables[i][j] : 1})

  # finding unallowed moves using all solutions to the now restricted bdd
  def findUnallowedMoves(self, n):
    allPossibleSol = list(self.constraintExpr.satisfy_all())
    sum_of_all = defaultdict(int)
    for i in allPossibleSol:
      for j in range(n):
        for k in range(n):
          try:
            sum_of_all[(j,k)] += i[self.bddVariables[j][k]]
          except KeyError:
            sum_of_all[(j,k)] += 1
    return list(filter(lambda idx: sum_of_all[idx]==0, sum_of_all))


"""class for solver
defines the logic layer + business layer
initialises the board, bdd and set  up the bdd for start
have upper lever functions - asking for move
"""
class nQueensSolver:
  def __init__(self, n = 8, hints = 1):
    self.n = n   # n can only b >= 4
    self.hint = hints
    self.board = nQueens(n)
    self.bdd = nQueensBDD(n)
    print('\n')
    print("Wait for the board.")
    # finding moves that are illegal from the start of the board(when n=4)
    self.board.disallowQueens(self.bdd.findUnallowedMoves(n))

  # ask for user input
  def askForMove(self, turn = 0):
    self.board.pprint()
    # if not n Queens and board not filled
    if (turn < self.n and self.board.spotLeft(self.n)):
      i, j = self.board.askInput(self.n, msg="Enter row and col for "+color.BOLD+color.BLUE+str(turn+1)+" queen"+color.END+".\nOr type "+color.BOLD+"help"+color.END+" for available commands: ")
      # putting queen on the board
      self.board.putQueen(i, j)
      # putting queen on the bdd - restriciting bdd
      self.bdd.putQueen(i, j)
      # changing the board using new bdd
      self.board.disallowQueens(self.bdd.findUnallowedMoves(self.n))
      turn += 1
      # n queens?
      if (turn == self.n):
        print(color.GREEN+color.BOLD+"SUCCESS"+color.END)
        print("Final Board.")
        self.board.pprint()
      else:
        # next turn
        self.askForMove(turn)
    else:
      print(color.BOLD+color.RED+"FAIL"+color.END)


if __name__ == '__main__':
  # For clearing part of screen
  # print(chr(27) + "[2J")
  n = int(input("Enter size of board ("+color.BOLD+">3"+color.END+"): "))
  if n>3:
    solver = nQueensSolver(n)
    solver.askForMove()
  else:
    print(color.BOLD+color.RED+"Board can't be solved. Exiting."+color.END)
