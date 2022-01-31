import keypad
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from JH_Lib import IMap, Enum, Mech, BitField, Cont
from JH_PixelMap import PixelMap
from HidUsage import USBKB as KB, USBKP as KP
        
class KeyMap(IMap):
    ''' Tuple of actions against an index which may be key numbers or code points in a string. The elements
        in the tuple may be:
        Positive Integer: A USB HID Key Code.
        Tuple of Positive Integer: Up to six similtaneous USB HID Key Codes, for example shifted codes.
        String: The code of each individual character is used as index in 'code_map' giving the USB HID codes.
        Callable: The element is called passing the action type (PRESS, RELEASE, SEND)
        None: Out of range index and explicit None elements are delegated to 'base_map' if specified.
    '''
    def __init__(self, map, base_map = None, code_map = None, first_index = 0):
        super().__init__(map, first_index)
        if base_map is not None and not isinstance(base_map, KeyMap): raise TypeError("Must be KeyMap")
        if code_map is not None and not isinstance(code_map, KeyMap): raise TypeError("Must be KeyMap")
        self._base_map = base_map
        self._code_map = code_map

    def action(self, act_func, act_type, ix=0):
        if act_type is ActionType.RELEASE_ALL:
            act_func(act_type)
            return
        code = self[ix]
        if type(code) is int or callable(code):
            act_func(act_type, code)
        elif type(code) is tuple:
            act_func(act_type, *code)
        if act_type not in (ActionType.PRESS, ActionType.SEND): return
        if type(code) is str and type(self._code_map) is KeyMap:
            kbs = act_func(ActionType.LED_STATE, 0)
            for ch in code:
                oc = ord(ch)
                self._code_map.action(act_func, ActionType.SEND, oc)
            act_func(ActionType.LED_STATE, kbs)

    def __getitem__(self, ix):
        cd = super().__getitem__(ix)
        if cd is not None: return cd
        if isinstance(self._base_map, KeyMap): cd = self._base_map[ix]
        if cd is not None: return cd
        return self.default

KEY_MAP_NULL = KeyMap(())
''' Dummy keymap with no entries used as 'do nothing' for unused chords below.
'''

class ChordMap(IMap):
    ''' Tuple of entries which may be KeyMap, None or a Tuple of KeyMap and a colour tuple.
        Indexed by the binary value of a chord of PKEYs (represented by BitFields)
        Maintains a record of the currently selected entry and a 'locked' entry which is
        restored to current by the 'reset' method. An optional 'notifier' method is called
        on a change of selection and passed BitFields of old and new chords and the colour
        corresponding to the new.
    '''
    def __init__(self, map, pkeys=4, initial=0):
        super().__init__(map)
        self._current = BitField(pkeys, initial)
        self._locked = BitField(pkeys, self._current)
        self._lk = False

    @property
    def current(self):
        return self._current 
    @current.setter
    def current(self, chord):
        if self._lk or self._current == chord: return
        self._current[:] = int(chord)
        if hasattr(self, 'notifier') and callable(self.notifier):
            m = self._map[int(self._current)]
            c = m[1] if isinstance(m, tuple) else (0,0,0)
            self.notifier(self._current, c)

    def lock(self):
        self._locked[:] = self._current
        self._lk = True

    def reset(self):
        self._lk = False
        self.current[:] = self._locked

    @property
    def keymap(self):
        m = self._map[int(self.current)]
        if isinstance(m, tuple): return m[0]
        if m is None: return KEY_MAP_NULL
        return m

class Side(Enum):
    ''' Enum recording if the primary multi-function keys are the right or left set.
    '''
    unassigned = Enum.v()
    left = Enum.v()
    right = Enum.v()

class KeyType(Enum):
    ''' Enum classifying key actions. 'l' and 'r' is left or right multi-function when Side is 'unassigned'.
        'p' and 's' are primary and secondary multi-function keys. 't' is typing key.
    '''
    allup = Enum.v()
    setix = Enum.v()
    ldown = Enum.v()
    lup = Enum.v()
    rdown = Enum.v()
    rup = Enum.v()
    pdown = Enum.v()
    pup = Enum.v()
    sdown = Enum.v()
    sup = Enum.v()
    tdown = Enum.v()
    tup = Enum.v()

class Leds(BitField):
    ''' BitField with one bit per state LED provided by the USB HID keyboard specification.
    '''
    NUM_LOCK = (0,1)
    CAPS_LOCK = (1,2)
    SCROLL_LOCK = (2,3)
    COMPOSE = (3,4)

    def __init__(self, val=0):
        super().__init__(4, val)

class ActionType(Enum):
    ''' Actions for the action_func callback which implements USB HID interface functionality. All match
        USB function names except added 'LED_STATE' which attempts to apply a given LED state and returns previous.
    '''
    RELEASE_ALL = Enum.v()
    PRESS = Enum.v()
    RELEASE = Enum.v() 
    SEND = Enum.v()
    LED_STATE = Enum.v()

class StateControl(Enum):

    MLK = Enum.v()  # Map Lock (Only makes sense in CFUNC as applies to currently selected PKEY chord)
    CMU = Enum.v()  # Chord Modifiers with Upper Multi-Functions (Only makes sense in an SFUNCS KeyMap)
    CML = Enum.v()  # Chord Modifiers with Lower Multi-Functions (Only makes sense in an SFUNCS KeyMap)

class KeyMech(Mech):
    ''' Implements the Keyboard State Machine. See separate state diagram for full documentation.
    '''
    def __init__(self, action_func, maps, debug = 0):
        super().__init__(KeyMech.init)
        self._action = action_func
        self._m = maps
        self._debug = debug

    def init(self, key_type, key_code):
        if key_type == KeyType.tdown:
            self._m.CHORDS.keymap.action(self._action, ActionType.PRESS, key_code)
        elif key_type == KeyType.tup:
            self._m.CHORDS.keymap.action(self._action, ActionType.RELEASE, key_code)
        elif key_type == KeyType.ldown:
            self._pside[:] = Side.left
            self._pchord[key_code] = 1
            self._ix = key_code
            return KeyMech.p
        elif key_type == KeyType.rdown:
            self._pside[:] = Side.right
            self._pchord[key_code] = 1
            self._ix = key_code
            return KeyMech.p
    def p(self, key_type, key_code):
        if key_type == KeyType.pup:
            self._m.PTAP.action(self._action, ActionType.SEND, key_code)
            self._pside[:] = Side.unassigned
            return KeyMech.init
        elif key_type == KeyType.tdown:
            self._pmods().action(self._action, ActionType.PRESS, self._ix)
            self._m.CHORDS.keymap.action(self._action, ActionType.PRESS, key_code)
            return KeyMech.pt
        elif key_type == KeyType.pdown:
            self._m.CHORDS.current = self._pchord
            return KeyMech.pp
        elif key_type == KeyType.sdown:
            self._m.SFUNCS[self._ix].action(self._action, ActionType.PRESS, key_code)
            return KeyMech.ps
    def pt(self, key_type, key_code):
        if key_type == KeyType.tdown:
            self._m.CHORDS.keymap.action(self._action, ActionType.PRESS, key_code)
            return
        elif key_type == KeyType.tup:
            self._m.CHORDS.keymap.action(self._action, ActionType.RELEASE, key_code)
            return
        elif key_type == KeyType.pup:
            self._pmods().action(self._action, ActionType.RELEASE, self._ix)
        self._pside[:] = Side.unassigned
        return KeyMech.init
    def ps(self, key_type, key_code):
        if self._ix >= 0:
            if key_type == KeyType.sup:
                self._m.SFUNCS[self._ix].action(self._action, ActionType.RELEASE, key_code)
            elif key_type == KeyType.sdown:
                self._m.SFUNCS[self._ix].action(self._action, ActionType.PRESS, key_code)
        else:
            if key_type == KeyType.pup:
                for i in range(0, 4):
                    if self._schord[i]:
                        self._smods().action(self._action, ActionType.PRESS, i)
                return KeyMech.s
    def s(self, key_type, key_code):
        if key_type == KeyType.sup:
            self._smods().action(self._action, ActionType.RELEASE, key_code)
        elif key_type == KeyType.tdown:
            self._m.CHORDS.keymap.action(self._action, ActionType.PRESS, key_code)
        elif key_type == KeyType.tup:
            self._m.CHORDS.keymap.action(self._action, ActionType.RELEASE, key_code)
        elif key_type == KeyType.pdown:
            if self._ix == -1:
                self._m.PTAP.action(self._action, ActionType.PRESS, key_code)
            else:
                self._m.UTAP.action(self._action, ActionType.PRESS, key_code)
        elif key_type == KeyType.pup:
            if self._ix == -1:
                self._m.PTAP.action(self._action, ActionType.RELEASE, key_code)
            else:
                self._m.UTAP.action(self._action, ActionType.RELEASE, key_code)
    def pp(self, key_type, key_code):
        if key_type in (KeyType.pup, KeyType.pdown):
            self._m.CHORDS.current = self._pchord
        elif key_type == KeyType.tdown:
            self._m.CHORDS.keymap.action(self._action, ActionType.PRESS, key_code)
        elif key_type == KeyType.tup:
            self._m.CHORDS.keymap.action(self._action, ActionType.RELEASE, key_code)
        elif key_type == KeyType.sdown:
            self._m.CFUNC.action(self._action, ActionType.PRESS, key_code)
        elif key_type == KeyType.sup:
            self._m.CFUNC.action(self._action, ActionType.RELEASE, key_code)

    def __pre__(self, key_type, key_code):
        if key_type == KeyType.allup: return KeyMech.init
        if self._pside != Side.unassigned:
            if key_type == KeyType.ldown:
                if self._pside == Side.left:
                    key_type[:] = KeyType.pdown
                else:
                    key_type[:] = KeyType.sdown
            elif key_type == KeyType.lup:
                if self._pside == Side.left:
                    key_type[:] = KeyType.pup
                else:
                    key_type[:] = KeyType.sup
            elif key_type == KeyType.rdown:
                if self._pside == Side.right:
                    key_type[:] = KeyType.pdown
                else:
                    key_type[:] = KeyType.sdown
            elif key_type == KeyType.rup:
                if self._pside == Side.right:
                    key_type[:] = KeyType.pup
                else:
                    key_type[:] = KeyType.sup
        if key_type == KeyType.pdown:
            self._pchord[key_code] = 1
        elif key_type == KeyType.sdown:
            self._schord[key_code] = 1
        elif key_type == KeyType.pup:
            self._pchord[key_code] = 0
        elif key_type == KeyType.sup:
            self._schord[key_code] = 0
    def __trans__(self, from_state, to_state):
        if self._debug > 1: print(from_state, " => ", to_state)
        if to_state is KeyMech.init:
            self._m.CHORDS.keymap.action(self._action, ActionType.RELEASE_ALL)
            self._m.CHORDS.reset()
            ix = 0
            self._pside[:] = Side.unassigned
            self._pchord[:] = False
            self._schord[:] = False
        return to_state

    def _pmods(self):
        return self._m.LMOD if self._pside == Side.left else self._m.RMOD
    def _smods(self):
        return self._m.RMOD if self._pside == Side.left else self._m.LMOD
    _pside = Side(Side.unassigned)
    _pchord = BitField(4)
    _schord = BitField(4)
    _ix = 0

class Usbkb:
    ''' Encapsulates the USB HID keyboard interface. 'update' must be called at intervals. The instance
        is called when a key change is detected. Provides 'action' callback to implement USB actions.
        The mapping of keys to functions is customisable in the class passed as 'maps'.
    '''
    def __init__(self, maps, debug = 0):
        self._maps = maps
        self._KB_State = KeyMech(self.action, maps, debug)
        self._kb = Keyboard(usb_hid.devices)
        self._kb_leds = Leds(self._kb.led_status[0])
        self._debug = debug

    def update(self):
        leds = self._kb.led_status
        if int(self._kb_leds) != leds[0]:
            self._kb_leds[0:4] = leds[0]
            if hasattr(self, 'notifier') and callable(self.notifier): self.notifier(self._kb_leds)

    def __call__(self, keytype, keycode):
        self._KB_State(keytype, keycode)

    def action(self, type, *codes):
        if len(codes) == 1 and callable(codes[0]):
            if type is not ActionType.PRESS: return
            if self._debug > 0:
                print("Usbkb.action", ActionType.class_state_name(type), StateControl.class_state_name(codes[0]))
            if codes[0] is StateControl.MLK:
                self._maps.CHORDS.lock()
            elif codes[0] is StateControl.CML:
                self._KB_State._ix = -1
            elif codes[0] is StateControl.CMU:
                self._KB_State._ix = -2
            return
        if self._debug > 0:
            print("Usbkb.action", ActionType.class_state_name(type), tuple(Cont.namein((KB,KP),v) for v in codes))
        if type is ActionType.RELEASE_ALL:
            self._kb.release_all()
        elif type is ActionType.PRESS:
            self._kb.press(*codes)
        elif type is ActionType.RELEASE:
            self._kb.release(*codes)
        elif type is ActionType.SEND:
            self._kb.send(*codes)
        elif type is ActionType.LED_STATE:
            self.update()
            os = self._kb_leds
            ds = Leds(codes[0])
            if ds == os: return ds
            if ds[Leds.NUM_LOCK] != os[Leds.NUM_LOCK]: self._kb.send(KP.NUMLK)
            if ds[Leds.CAPS_LOCK] != os[Leds.CAPS_LOCK]: self._kb.send(KB.CPLK)
            if ds[Leds.SCROLL_LOCK] != os[Leds.SCROLL_LOCK]: self._kb.send(KB.SCLK)
            if ds[Leds.COMPOSE] != os[Leds.COMPOSE]: self._kb.send(KB.APP)
            return int(ds)

    @property
    def leds(self):
        return self._kb_leds

class Orthokb:
    ''' Encapsulates the hardware interface comprising a matrix of keywsitches with diodes and a chain
        of Neopixel LEDs. The hardware layout is specified in the class passed as 'maps'. 'target' must
        be an instance of 'usbkb'.
    '''
    def __init__(self, target, maps, debug = 0):
        self._target = target
        self._m = maps
        self._keytype = KeyType(KeyType.allup)
        self._keys = keypad.KeyMatrix(
            row_pins=maps.ROWPINS,
            column_pins=maps.COLPINS,
            columns_to_anodes=False,
        )
        px = neopixel.NeoPixel(
            maps.NEOPIXEL,
            48,
            brightness=maps.PIXBRIGHT,
            auto_write=False
        )
        self._pixels = PixelMap(px, maps.MAP2PIX)
        self._pixels.fill()
        self._pixels.show()
        self._kd = 0
        self._debug = debug

    def update(self):
        key_event = self._keys.events.get()
        if key_event:
            k = self._m.KEY2MAP[key_event.key_number]
            m = self._m.MKEYMAP[k]
            if key_event.pressed:
                self._kd += 1
                if m == 0:
                    self._keytype[:] = KeyType.tdown
                elif m < 0:
                    self._keytype[:] = KeyType.rdown
                    k = (m * -1) - 1
                else:
                    self._keytype[:] = KeyType.ldown
                    k = m - 1
            else:
                self._kd -= 1
                if m == 0:
                    self._keytype[:] = KeyType.tup
                elif m < 0:
                    self._keytype[:] = KeyType.rup
                    k = (m * -1) - 1
                else:
                    self._keytype[:] = KeyType.lup
                    k = m - 1
            self._target(self._keytype, k)
            if self._kd < 1:
                self._kd = 0
                self._keytype[:] = KeyType.allup
                self._target(self._keytype, k)

    @property
    def pixels(self):
        return self._pixels
