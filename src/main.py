from copy import deepcopy

class Symbol:
  def __init__(self, symbol):
    self.symbol = symbol

  def __eq__(self, other):
    return self.symbol == other.symbol and self.isTerminal() == other.isTerminal()

  def __ne__(self, other):
    return not self == other

  def __str__(self):
    return self.symbol

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
    #return self.variableCount() < other.variableCount()
    return len(self.symbols) < len(other.symbols)

  def __eq__(self, other):
    if len(self.symbols) != len(self.symbols):
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
    if production.head not in self.symbols:
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
    if self.dotAtEnd:
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
        if x not in itemSet:
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

def CanonicalLR_0(starting, productions):
  pass

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

  """cnt = 0
  for s in enumerate(E, ps):
    print(s)
    cnt += 1
    if cnt > 500:
      exit(0)"""

  p11 = Production(E, s1)

  I1 = Item.fromProduction(p1, 0)
  I2 = Item.fromProduction(p11, 2)

  S = {I1}
  print(S)
  S.add(I2)
  print(S)
  for s in S:
    print(s)

def main():
  test()

if __name__ == "__main__":
  main()