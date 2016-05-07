from copy import deepcopy

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

  (NtoI, trans) = CanonicalLR_0(E, ps)
  for i in range(len(NtoI)):
    print('#', i)
    printSet(NtoI[i])
    print()

def main():
  test()

if __name__ == "__main__":
  main()