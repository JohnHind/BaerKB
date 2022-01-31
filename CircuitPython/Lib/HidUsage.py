'''
Universal Serial Bus (USB) HID Usage Tables V1.12
https://usb.org/document-library/hid-usage-tables-122
'''

from JH_Lib import Cont

class USBKB(Cont):
    ''' Keyboard Page (0x07) Kaypad and non-PC, non-Mac excluded
    '''
    A = 0x04    # Letters
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D
    D1 = 0x1E   # 1 and !
    D2 = 0x1F   # 2 and " (US @)
    D3 = 0x20   # 3 and £ (US #)
    D4 = 0x21   # 4 and $
    D5 = 0x22   # 5 and %
    D6 = 0x23   # 6 and ^
    D7 = 0x24   # 7 and &
    D8 = 0x25   # 8 and *
    D9 = 0x26   # 9 and (
    D0 = 0x27   # 0 and )
    ENT = 0x28  # CR/Enter
    ESC = 0x29  # Escape
    BS = 0x2A   # Destructive Backspace
    TAB = 0x2B
    SP = 0x2C   # Spacebar
    MINUS = 0x2D    # - and _
    EQ = 0x2E       # = and +
    OBRCE = 0x2F    # [ and {
    CBRCE = 0x30    # ] and }
    BSLSH = 0x31    # \ and |
    HASH = 0x32     # Non-US # and ~
    SEMIC = 0x33    # ; and :
    QUOTE = 0x34    # ' and @ (US ")
    GRAVE = 0x35    # ` and ¬ (US ~)
    COMMA = 0x36    # , and <
    FSTOP = 0x37    # . and >
    FSLSH = 0x38    # / and ?
    CPLK = 0x39     # Caps Lock
    F1 = 0x3A   # Function Keys
    F2 = 0x3B
    F3 = 0x3C
    F4 = 0x3D
    F5 = 0x3E
    F6 = 0x3F
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45
    PRTSC = 0x46    # Print Screen
    SCLK = 0x47     # Scroll Lock
    PAUSE = 0x48
    INS = 0x49
    HOME = 0x4A
    PGUP = 0x4B
    DEL = 0x4C
    END = 0x4D
    PGDN = 0x4E
    RIGHT = 0x4F
    LEFT = 0x50
    DOWN = 0x51
    UP = 0x52
    NBKSL = 0x64     # Non-US \ and |
    APP = 0x65
    PWR = 0x66
    F13 = 0x68  # More Function Keys
    F14 = 0x69
    F15 = 0x6A
    F16 = 0x6B
    F17 = 0x6C
    F18 = 0x6D
    F19 = 0x6E
    F20 = 0x6F
    F21 = 0x70
    F22 = 0x71
    F23 = 0x72
    F24 = 0x73
    LCTL = 0xE0 # Modifier Keys
    LSFT = 0xE1
    LALT = 0xE2
    LGUI = 0xE3
    RCTL = 0xE4
    RSFT = 0xE5
    RALT = 0xE6
    RGUI = 0xE7

class USBKP(Cont):
    ''' Keypad Page (0x07) Kayboard and non-PC, non-Mac excluded
    '''
    NUMLK = 0x53    # Num Lock and Clear
    SLASH = 0x54
    STAR = 0x55
    MINUS = 0x56
    PLUS = 0x57
    ENT = 0x58
    D1 = 0x59       # 1 and End
    D2 = 0x5A       # 2 and Down
    D3 = 0x5B       # 3 and PgDn
    D4 = 0x5C       # 4 and Left
    D5 = 0x5D
    D6 = 0x5E       # 6 and Right
    D7 = 0x5F       # 7 and Home
    D8 = 0x60       # 8 and Up
    D9 = 0x61       # 9 and PgUp
    D0 = 0x62       # 0 and Ins
    DP = 0x63       # . and Del
    EQ = 0x67

class USBCO:
    ''' Composite Codes for shifted punctuation & adaptive Codes for US/Non-US
    '''
    def __init__(self, us=False, apple=False):
        self._us = us
        self._ap = apple

    @property
    def GRAVE(self):
        if self._ap: return USBKB.BSLSH if self._us else USBKB.NBKSL
        return USBKB.GRAVE

    @property
    def HASH(self):
        return (USBKB.LSFT, USBKB.D3) if self._us else USBKB.HASH

    @property
    def TILD(self):
        return (USBKB.LSFT, USBKB.GRAVE) if self._us else (USBKB.LSFT, USBKB.HASH)

    @property
    def BSLSH(self):
        if self._ap: return USBKB.GRAVE
        return USBKB.BSLSH if self._us else USBKB.NBKSL

    @property
    def PIPE(self):
        if self._ap: return (USBKB.LSFT, USBKB.GRAVE)
        return (USBKB.LSFT, USBKB.BSLSH) if self._us else (USBKB.LSFT, USBKB.NBKSL)

    @property
    def DQOT(self):
        return (USBKB.LSFT, USBKB.QUOTE) if self._us else (USBKB.LSFT, USBKB.D2)

    @property
    def NOTS(self):
        if self._ap: return (USBKB.LSFT, USBKB.BSLSH) if self._us else (USBKB.LSFT, USBKB.NBKSL)
        return None if self._us else (USBKB.LSFT, USBKB.GRAVE)

    @property
    def AT(self):
        return (USBKB.LSFT, USBKB.D2) if self._us else (USBKB.LSFT, USBKB.QUOTE)

    USCORE = (USBKB.LSFT, USBKB.MINUS)

    PLUS = (USBKB.LSFT, USBKB.EQ)

    OCURL = (USBKB.LSFT, USBKB.OBRCE)

    CCURL = (USBKB.LSFT, USBKB.CBRCE)

    COLON = (USBKB.LSFT, USBKB.SEMIC)

    OANG = (USBKB.LSFT, USBKB.COMMA)

    CANG = (USBKB.LSFT, USBKB.FSTOP)

    QMK = (USBKB.LSFT, USBKB.FSLSH)

    EXCM = (USBKB.LSFT, USBKB.D1)

    DOLR = (USBKB.LSFT, USBKB.D4)

    PCNT = (USBKB.LSFT, USBKB.D5)

    CRT = (USBKB.LSFT, USBKB.D6)

    AMPS = (USBKB.LSFT, USBKB.D7)

    STAR = (USBKB.LSFT, USBKB.D8)

    OBKT = (USBKB.LSFT, USBKB.D9)

    CBKT = (USBKB.LSFT, USBKB.D0)

