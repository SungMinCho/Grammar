from copy import deepcopy
from graphviz import *

def setToString(s):
  return '\n'.join([x.__str__() for x in s])

def printSet(s):
  for x in s:
    print(x)

def inDeep(x, l):
  for y in l:
    if x == y:
      return True
  return False

def setEqual(s1, s2):
  for x in s1:
    if not inDeep(x, s2):
      return False

  for x in s2:
    if not inDeep(x, s1):
      return False

  return True

def inDeepSet(s, ss):
  for s2 in ss:
    if setEqual(s, s2):
      return True
  return False

def findKeyByValue(v, d):
  for k in d:
    if d[k] == v:
      return k
  return None

def findKeyByValueSet(v, d):
  for k in d:
    if setEqual(d[k],v):
      return k
  return None

####################################################################################

class Symbol:
  def __init__(self, symbol):
    self.symbol = symbol

  def __eq__(self, other):
    return self.symbol == other.symbol and self.isTerminal() == other.isTerminal()

  def __ne__(self, other):
    return not self == other

  def __str__(self):
    return self.symbol

  def __hash__(self):
    return hash(self.__dict__.values())

  def isTerminal(self):
    return True

class Terminal(Symbol):
  pass

class Variable(Symbol):
  def isTerminal(self):
    return False

class String:
  def __init__(self, symbols):
    self.symbols = symbols

  def __str__(self):
    return " ".join([s.__str__() for s in self.symbols])

  def clone(self):
    return String(deepcopy(self.symbols))

  # order by number of symbols
  def __lt__(self, other):
    return len(self.symbols) < len(other.symbols)

  def __eq__(self, other):
    if len(self.symbols) != len(other.symbols):
      return False
    for i in range(len(self.symbols)):
      if self.symbols[i] != other.symbols[i]:
        return False
    return True

  def __ne__(self, other):
    return not self == other

  def allTerminal(self):
    for s in self.symbols:
      if not s.isTerminal():
        return False
    return True

  def variableCount(self):
    cnt = 0
    for s in self.symbols:
      if not s.isTerminal():
        cnt += 1
    return cnt

  def applyProduction(self, production):
    if not inDeep(production.head, self.symbols):
      return False
    i = self.symbols.index(production.head)
    self.symbols = self.symbols[:i] + production.body.symbols + self.symbols[i+1:]
    return True

class Production:
  def __init__(self, head, body):
    # head is Symbol. body is String
    self.head = head
    self.body = body

  def __eq__(self, other):
    return self.head == other.head and self.body == other.body

  def __ne__(self, other):
    return not self == other

  def __hash__(self):
    return hash(self.__dict__.values())

  def __str__(self):
    return self.head.__str__() + " -> " + self.body.__str__()

class Item(Production):
  def __init__(self, head, body, dot):
    Production.__init__(self, head, body)
    self.dot = dot

  def fromProduction(production, dot):
    return Item(production.head, production.body, dot)

  # if A -> a . X b   then yield all X -> . c
  def closureStep(self, productions):
    if self.dot < len(self.body.symbols):
      X = self.body.symbols[self.dot]
      if not X.isTerminal():
        for p in productions:
          if p.head == X:
            yield Item.fromProduction(p, 0)

  def dotAtEnd(self):
    return self.dot >= len(self.body.symbols)

  def nextIs(self, X):
    if self.dotAtEnd():
      return False
    return X == self.body.symbols[self.dot]

  def moveDotToRight(self):
    return Item(self.head, self.body, self.dot + 1)

  def __eq__(self, other):
    return Production.__eq__(self, other) and self.dot == other.dot

  def __ne__(self, other):
    return not self == other

  def __hash__(self):
    return hash(self.__dict__.values())

  def __str__(self):
    s = [s.__str__() for s in self.body.symbols]
    s[self.dot:self.dot] = "."
    s = " ".join(s)
    return self.head.__str__() + " -> " + s

####################################################################################

def insertPosition(string, strings):
  for i in range(len(strings)):
    if string < strings[i]:
      return i
  return len(strings)

# buffer = string, productions = list of Production
def produceOneStep(string, productions):
  res = []
  temp = string.clone()
  for production in productions:
    if temp.applyProduction(production):
      yield temp
      temp = string.clone()

def enumerate(starting, productions):
  strings = [String([starting])]
  while len(strings) > 0:
    #print("list")
    #for s in strings:
    #  print(s)
    #print("end")
    #print()
    h = strings.pop(0)
    if h.allTerminal():
      yield h
    else:
      for s in produceOneStep(h, productions):
        i = insertPosition(s, strings)
        strings[i:i] = [s]

####################################################################################

def closure(itemSet, productions):
  while True:
    buffer = []
    for s in itemSet:
      for x in s.closureStep(productions):
        if not inDeep(x, itemSet) and not inDeep(x, buffer):
          buffer.append(x)

    if len(buffer) == 0:
      return itemSet

    for b in buffer:
      itemSet.add(b)

def goto(itemSet, X, productions):
  res = set()
  for s in itemSet:
    if s.nextIs(X):
      res.add(s.moveDotToRight())
  return closure(res, productions)

def grammarSymbols(productions):
  res = set()
  for p in productions:
    res.add(p.head)
    for s in p.body.symbols:
      res.add(s)
  return res

def CanonicalLR_0(starting, productions):
  syms = grammarSymbols(productions)

  NumberToItems = {}
  transition = []
  dummyname = starting.symbol + "'"
  if dummyname in syms:
    dummyname = "dummy" + starting.symbol
  if dummyname in syms:
    assert(False and "dummyname already exists")
  dummyStart = Variable(dummyname)
  dummyItem = Item(dummyStart, String([starting]), 0)
  initial = {dummyItem}
  initial = closure(initial, productions)


  cnt = 0
  buffer = [(initial, 0)]

  while len(buffer) > 0:
    (h,num) = buffer.pop(0)

    NumberToItems[num] = h

    for sym in syms:
      g = goto(h, sym, productions)
      if len(g) > 0:
        if inDeepSet(g, NumberToItems.values()):
          num2 = findKeyByValueSet(g, NumberToItems)
        elif inDeepSet(g, [x[0] for x in buffer]):
          num2 = 0
          for x in buffer:
            if x[0] == g:
              num2 = x[1]
              break
        else:
          cnt += 1
          num2 = cnt
          buffer.append((g, num2))
        transition.append((num, sym, num2))

  return (NumberToItems, transition)

def draw_CanonicalLR_0(starting, productions):
  (NumberToItems, transition) = CanonicalLR_0(starting, productions)
  dot = Digraph()

  for (k,v) in NumberToItems.items():
    dot.node(str(k), setToString(v))

  for (From,Sym,To) in transition:
    dot.edge(str(From), str(To), label=Sym.__str__())

  dot.render('result.dot', view=True)


####################################################################################

def test():
  T = Variable("T")
  E = Variable("E")
  INT = Terminal("int")
  plus = Terminal("+")
  mult = Terminal("*")
  div = Terminal("/")
  lparen = Terminal("(")
  rparen = Terminal(")")

  s1 = String([T, plus, E])
  s2 = String([T])
  s3 = String([INT, mult, T])
  s4 = String([INT])
  s5 = String([lparen, E, rparen])

  p1 = Production(E, s1)
  p2 = Production(E, s2)
  p3 = Production(T, s3)
  p4 = Production(T, s4)
  p5 = Production(T, s5)

  ps = [p1,p2,p3,p4, p5]

  draw_CanonicalLR_0(E, ps)

def snupl_test():
  CHAR = Terminal("char")
  STRING = Terminal("string")
  IDENT = Terminal("ident")
  NUMBER = Terminal("number")
  BOOLEAN = Terminal("boolean")
  TYPE = Variable("type")
  BASETYPE = Terminal("basetype")
  LBRAK = Terminal("\"[\"")
  RBRAK = Terminal("\"]\"")
  QUALIDENT = Variable("qualident")
  EXPRESSION = Variable("expression")
  FACTOP = Terminal("factOp")
  RELOP = Terminal("relOp")
  FACTOR = Variable("factor")
  LPAREN = Terminal("\"(\"")
  RPAREN = Terminal("\")\"")
  NOT = Terminal("\"!\"")
  SUBROUTINECALL = Variable("subroutineCall")
  TERM = Variable("term")
  SIMPLEEXPR = Variable("simpleexpr")
  ASSIGNMENT = Variable("assignment")
  IFSTATEMENT = Variable("ifStatement")
  WHILESTATEMENT = Variable("whileStatement")
  RETURNSTATEMENT = Variable("returnStatement")
  STATEMENT = Variable("statement")
  ASSIGN = Terminal("\":=\"")
  STATSEQUENCE = Variable("statSequence")
  IF = Terminal("\"if\"")
  THEN = Terminal("\"then\"")
  ELSE = Terminal("\"else\"")
  DO = Terminal("\"do\"")
  BEGIN = Terminal("\"begin\"")
  END = Terminal("\"end\"")
  WHILE = Terminal("\"while\"")
  RETURN = Terminal("\"return\"")
  SEMICOLON = Terminal("\";\"")
  COLON = Terminal("\":\"")
  VARDECLARATION = Variable("varDeclaration")
  VARDECLSEQUENCE = Variable("varDeclSequence")
  VARDECL = Variable("varDecl")
  SUBROUTINEDECL = Variable("subroutineDecl")
  PROCEDUREDECL = Variable("procedureDecl")
  FUNCTIONDECL = Variable("functionDecl")
  FORMALPARAM = Variable("formalParam")
  SUBROUTINEBODY = Variable("subroutineBody")
  VAR = Terminal("\"var\"")
  PROCEDURE = Terminal("\"procedure\"")
  FUNCTION = Terminal("\"function\"")
  MODULE = Variable("module")
  TERMINALMODULE = Terminal("\"module\"")
  DOT = Terminal("\".\"")

  TERMOP = Variable("termOp") # because of ["+" | "-"]
  PLUS = Terminal("\"+\"")
  MINUS = Terminal("\"-\"")
  OR = Terminal("\"||\"")
  pt1 = Production(TERMOP, String([PLUS]))
  pt2 = Production(TERMOP, String([MINUS]))
  pt3 = Production(TERMOP, String([OR]))

  p1 = Production(TYPE, String([BASETYPE]))
  p2 = Production(TYPE, String([TYPE, LBRAK, NUMBER, RBRAK]))
  p3 = Production(TYPE, String([TYPE, LBRAK, RBRAK]))
  p4 = Production(QUALIDENT, String([IDENT]))
  p5 = Production(QUALIDENT, String([QUALIDENT, LBRAK, EXPRESSION, RBRAK]))
  p6 = Production(FACTOR, String([QUALIDENT]))
  p7 = Production(FACTOR, String([NUMBER]))
  p8 = Production(FACTOR, String([BOOLEAN]))
  p9 = Production(FACTOR, String([CHAR]))
  p10 = Production(FACTOR, String([STRING]))
  p11 = Production(FACTOR, String([LPAREN, EXPRESSION, RPAREN]))
  p12 = Production(FACTOR, String([SUBROUTINECALL]))
  p13 = Production(FACTOR, String([NOT, FACTOR]))
  p14 = Production(TERM, String([FACTOR]))
  p15 = Production(TERM, String([TERM, FACTOP, FACTOR]))
  p16 = Production(SIMPLEEXPR, String([TERM]))
  p17 = Production(SIMPLEEXPR, String([PLUS, TERM]))
  p18 = Production(SIMPLEEXPR, String([MINUS, TERM]))
  p19 = Production(SIMPLEEXPR, String([SIMPLEEXPR, TERMOP, TERM]))
  p20 = Production(EXPRESSION, String([SIMPLEEXPR]))
  p21 = Production(EXPRESSION, String([SIMPLEEXPR, RELOP, SIMPLEEXPR]))
  p22 = Production(ASSIGNMENT, String([QUALIDENT, ASSIGN, EXPRESSION]))
  # add EXPRESSIONS...
  EXPRESSIONS = Variable("expressions")
  COMMA = Terminal("\",\"")
  p24_1 = Production(EXPRESSIONS, String([EXPRESSION]))
  p24_2 = Production(EXPRESSIONS, String([EXPRESSIONS, COMMA, EXPRESSION]))
  p23 = Production(SUBROUTINECALL, String([IDENT, LPAREN, RPAREN]))
  p24 = Production(SUBROUTINECALL, String([IDENT, LPAREN, EXPRESSIONS, RPAREN]))

  p25 = Production(IFSTATEMENT, String([IF, LPAREN, EXPRESSION, RPAREN, THEN, STATSEQUENCE, END]))
  p26 = Production(IFSTATEMENT, String([IF, LPAREN, EXPRESSION, RPAREN, THEN, STATSEQUENCE, ELSE, STATSEQUENCE, END]))

  p27 = Production(WHILESTATEMENT, String([WHILE, LPAREN, EXPRESSION, RPAREN, DO, STATSEQUENCE, END]))

  p28 = Production(RETURNSTATEMENT, String([RETURN]))
  p29 = Production(RETURNSTATEMENT, String([RETURN, EXPRESSION]))

  p30 = Production(STATEMENT, String([ASSIGNMENT]))
  p31 = Production(STATEMENT, String([SUBROUTINECALL]))
  p32 = Production(STATEMENT, String([IFSTATEMENT]))
  p33 = Production(STATEMENT, String([WHILESTATEMENT]))
  p34 = Production(STATEMENT, String([RETURNSTATEMENT]))

  p35 = Production(STATSEQUENCE, String([])) # MIGHT CAUSE TROUBLE??? TODO???
  p36 = Production(STATSEQUENCE, String([STATEMENT]))
  p37 = Production(STATSEQUENCE, String([STATSEQUENCE, SEMICOLON, STATEMENT]))

  p38 = Production(VARDECLARATION, String([]))
  p39 = Production(VARDECLARATION, String([VAR, VARDECLSEQUENCE, SEMICOLON]))

  p40 = Production(VARDECLSEQUENCE, String([VARDECL]))
  p41 = Production(VARDECLSEQUENCE, String([VARDECLSEQUENCE, SEMICOLON, VARDECL]))

  # add IDENTS
  IDENTS = Variable("idents")
  p42_1 = Production(IDENTS, String([IDENT]))
  p42_4 = Production(IDENTS, String([IDENTS, COMMA, IDENT]))
  p42 = Production(VARDECL, String([IDENTS, COLON, TYPE]))

  p43 = Production(SUBROUTINEDECL, String([PROCEDUREDECL, SUBROUTINEBODY, IDENT, SEMICOLON]))
  p44 = Production(SUBROUTINEDECL, String([FUNCTIONDECL, SUBROUTINEBODY, IDENT, SEMICOLON]))

  p45 = Production(PROCEDUREDECL, String([PROCEDURE, IDENT, SEMICOLON]))
  p46 = Production(PROCEDUREDECL, String([PROCEDURE, IDENT, FORMALPARAM, SEMICOLON]))

  p47 = Production(PROCEDUREDECL, String([FUNCTION, IDENT, COLON, TYPE, SEMICOLON]))
  p48 = Production(PROCEDUREDECL, String([FUNCTION, IDENT, FORMALPARAM, COLON, TYPE, SEMICOLON]))

  p49 = Production(FORMALPARAM, String([LPAREN, RPAREN]))
  p50 = Production(FORMALPARAM, String([LPAREN, VARDECLSEQUENCE, RPAREN]))

  p51 = Production(SUBROUTINEBODY, String([VARDECLARATION, BEGIN, STATSEQUENCE, END]))

  # add SUBROUTINEDECLS
  SUBROUTINEDECLS = Variable("subroutineDecls")
  p52_1 = Production(SUBROUTINEDECLS, String([]))
  p52_2 = Production(SUBROUTINEDECLS, String([SUBROUTINEDECL]))
  p52_3 = Production(SUBROUTINEDECLS, String([SUBROUTINEDECLS, SUBROUTINEDECL]))
  p52 = Production(MODULE, String([TERMINALMODULE, IDENT, SEMICOLON, VARDECLARATION, SUBROUTINEDECLS, BEGIN, STATSEQUENCE, END, IDENT, DOT]))

  ps = [pt1,pt2,pt3,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24_1,p24_2,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,\
        p34,p35,p36,p37,p38,p39,p40,p41,p42_1,p42_2,p42,p43,p44,p45,p46,p47,p48,p49,p50,p51,p52_1,p52_2,p52_3,p52]

  draw_CanonicalLR_0(MODULE, ps)

def main():
  snupl_test()

if __name__ == "__main__":
  main()
