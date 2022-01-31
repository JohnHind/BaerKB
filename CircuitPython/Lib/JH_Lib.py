class Enum:
    ''' Base Class for mutable enumerated types.
    '''
    def __init__(self, init_state):
        self.state_name(init_state)
        self.state = init_state

    def __repr__(self):
        return f"{type(self)}({self.state_name()})"

    def __str__(self):
        return f"Enum{type(self)} State: {self.state_name()}"

    def __setitem__(self, ix, val):
        if not isinstance(ix, slice) or ix.start != None or ix.stop != None or ix.step != None:
            raise IndexError("Enum only supports reference form [:] to set the state")
        self.state = val

    def __eq__(self, other):
        if isinstance(other, Enum):
            return self.state is other.state
        else:
            return self.state is other

    @staticmethod
    def v():
        def f(*p,**k): pass
        return f

    def state_name(p1, p2=None):
        cls = p1 if isinstance(p1, type) else type(p1)
        state = p2 if p2 is not None else p1.state
        if callable(state):
            for k,v in cls.__dict__.items():
                if state is v and not k.startswith("_"): return k
        raise RuntimeError(f"State must be a method of {cls}")

    @classmethod
    def class_state_name(cls, state):
        return cls.state_name(cls, state)
'''
class MyEnum(Enum):
    monday = Enum.v()
    tuesday = Enum.v()
    wednesday = Enum.v()

day1 = MyEnum(MyEnum.tuesday)
print(day1.state_name())
print(day1.state_name(MyEnum.monday))
print(MyEnum.state_name(MyEnum, MyEnum.wednesday))
print(MyEnum.class_state_name(MyEnum.wednesday))
day2 = MyEnum(MyEnum.wednesday)
print(day1, day2, day1 == day2, day1 == MyEnum.tuesday)
day1[:] = MyEnum.wednesday
print(day1, day2, day1 == day2, day1 == MyEnum.tuesday)
'''

class Mech(Enum):
    ''' Base Class for State Machines.
    '''
    def __call__(self, *pargs, **nargs):
        cs = True
        if hasattr(self, "__pre__"):
            ns = self.__pre__(*pargs, **nargs)
            cs = not callable(ns) or ns is self.state
        if cs:
            ns = self.state(self, *pargs, **nargs)
            if not ns: return
        if callable(ns) and ns is not self.state:
            if hasattr(self, "__trans__"): ns = self.__trans__(self.state, ns)
        if not callable(ns):raise RuntimeError(f"Mech Error: {ns}")
        self.state = ns
'''
class MyMech(Mech):
    def state1(self, i):
        print(self.state_name(), i)
        if i < 12: return
        return MyMech.state2
    def state2(self, i):
        print(self.state_name(), i)
        if i == 19: return "Error in MyMech"
        return MyMech.state1

    def __pre__(self, i):
        print("Optional common pre-processing", i)
    def __trans__(self, from_state, to_state):
        print("Optional state transition trap", self.state_name(from_state), "to", self.state_name(to_state))
        return to_state

mymech = MyMech(MyMech.state1)
print(mymech)
for i in range(10, 20): mymech(i)
'''

class BitField:
    ''' Mutable set-width non-negative integer with bit indexing and iteration.
        Useful for mapping hardware registers and for assembling and serialising protocol packets.
    '''
    def __init__(self, width, field=False, word=None):
        self.width = int(width)
        bw = self.width // 8
        if self.width % 8: bw += 1
        self.field = bytearray(bw)
        self.__setitem__((0,self.width), field)
        if word: self.word = word

    def __int__(self):
        x = 0
        for i in range(0, len(self.field)): x += self.field[i] << (i * 8)
        return x

    def __bool__(self):
        return self.__int__() != 0

    def __len__(self):
        return self.width

    def __bytes__(self):
        return bytes(self.field)

    def __str__(self):
        s = BitField.bin(self.__int__(), self.width)
        if len(s) > 10: s = "..." + s[0:10]
        return f"BitField:[{s}]"

    def __repr__(self):
        return self.__str__()

    def __index__(self):
        return self.__int__

    def __eq__(self, other):
        return self.__int__ == int(other)

    def __getitem__(self, ix):
        st, sp = self._normix(ix)
        sp -= 1
        stb = st // 8
        spb = sp // 8
        y = 0
        p = 0
        for i in range(stb, spb + 1):
            x = self.field[i]
            if i == spb: x &= 2 ** (sp % 8 + 1) - 1
            y |= x << p
            p += 8
        y >>= (st % 8)
        return y

    def __setitem__(self, ix, val):
        st, sp = self._normix(ix)
        sp -= 1
        stb = st // 8
        spb = sp // 8
        fs = True
        if isinstance(val, bool):
            if val: val = 0xFF 
            else: val = 0
            fs = False
        else:
            val = int(val)
        for i in range(stb, spb + 1):
            src_byte = val & 0xFF
            if fs: val >>= 8
            msk = 0xFF
            if i == stb:
                src_byte <<= (st % 8)
                src_byte &= 0xFF
                msk &= 2 ** (st % 8) - 1
            if i == spb:
                m = 2 ** (sp % 8 + 1) - 1
                src_byte &= m
                msk |= m ^ 0xFF
            self.field[i] &= msk
            self.field[i] |= src_byte

    def __iter__(self):
        if hasattr(self, 'word') and self.word < 0:
            self._p = self.width + self.word
        else:
            self._p = 0
        return self

    def __next__(self):
        if self._p >= self.width or self._p < 0: raise StopIteration
        st = self._p
        sp = st + 1
        if hasattr(self, 'word'):
            if self.word < 0:
                sp = st - self.word
            else:
                sp = st + self.word
            self._p += self.word
        else:
            self._p += 1
        return self.__getitem__((st, sp))

    @staticmethod
    def bin(val, width=8):
        #return f"{val:b}".zfill(width)  # zfill is not available in CircuitPython!
        s = f"{val:b}"
        return '0' * (width - len(s)) + s

    def _normix(self, ix):
        if isinstance(ix, slice):
            sp = ix.stop
            ix = ix.start
            if not isinstance(ix, int): ix = 0
            if ix < 0: ix = ix + self.width
            if not isinstance(sp, int): sp = self.width
            if sp < 0: sp = sp + self.width
        elif isinstance(ix, tuple):
            sp = int(ix[1])
            ix = int(ix[0])
        else:
            ix = int(ix)
            if ix < 0: ix += self.width
            sp = ix + 1
        if ix >= self.width or sp > self.width or ix < 0 or sp <= ix:
            raise IndexError(f"Invalid Bitfield index {ix}, {sp}")
        return ix, sp
'''
class MyBitField(BitField):
    # not essential to sub-class BitField, but allows for named ranges within the field
    def __init__(self):
        BitField.__init__(self, 32, word=8)
        # Field 32 bits wide, initialised all 0, iteration produces 8 bit words little end first.
        # can use a negative word size to produce big end first. Specify 'field' to initialise
        # either to an integer constant or True to initialise all bits set.
    flag1 = (0,1)
    flag2 = (1,2)
    counter = (2,10)

myfield = MyBitField()
print(myfield)
myfield[myfield.flag1] = 1
myfield[myfield.counter] = 0b1010101011
myfield[30:32] = 0b11
print(myfield)
print(BitField.bin(myfield[myfield.counter], 8))
for w in myfield: print(BitField.bin(w, 8), end=', ')
print()
'''

class IMap:
    ''' Tuple with configurable base index and defaults for index under, index over and value None.
    '''
    def __init__(self, map, first_index=0, default=None, default_under=None, default_over=None):
        if not isinstance(map, tuple): raise TypeError("IMap requires a Tuple of map outputs")
        self._map = map
        self.first_index = int(first_index)
        self.default = default
        self.default_under = default_under if default_under is not None else default
        self.default_over = default_over if default_over is not None else default_under if default_under is not None else default

    def __getitem__(self, ix):
        ix = int(ix) - self.first_index
        if ix < 0: return self.default_under
        if ix >= len(self._map): return self.default_over
        r = self._map[ix]
        if r is None: return self.default
        return r

    def __len__(self):
        return len(self._map)

'''
mymap = IMap(("first","second","third"), 2, "outside")
for i in range(1,6): print(mymap[i], end=', ')
print()
mymap = IMap(("first","second","third"), default_under="under", default_over="over")
for i in range(-1,4): print(mymap[i], end=', ')
print()
mymap = IMap(("first",None,"third"), default="missing", default_under="under", default_over="over")
for i in range(-1,4): print(mymap[i], end=', ')
print()
mymap = IMap(("first",None,"third"), default="missing")
for i in range(-1,4): print(mymap[i], end=', ')
'''

class Cont:
    ''' Base Class for classes used as dictionary-like container were elements are member variables.
        Efficient for storage of a fixed set of variables or constants with mainly forward lookup.
        Inefficient reverse lookup is provided primarily for diagnostic and debug reports.
    '''
    @classmethod
    def nameof(cls, val):
        ''' Reverse lookup in the class
        '''
        for k,v in cls.__dict__.items():
            if v == val: return k
        return val

    @staticmethod
    def namein(clss, val):
        ''' Reverse lookup over a list of classes sharing this base
        '''
        for cls in clss:
            for k,v in cls.__dict__.items():
                if v == val: return f"{cls.__name__}.{k}"
        return val
'''
class D1(Cont):
    ONE = 1
    TWO = 2
    THREE = 3

class D2(Cont):
    TEN = 10
    TWENTY = 20
    THIRTY = 30

print(D1.TWO, D2.THIRTY)
print(D1.nameof(2), Cont.namein((D1,D2), 20))
'''
