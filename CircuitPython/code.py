import time
import board, digitalio
from JH_Lib import IMap
from JH_PixelMap import PixelMap
from Ortho import KeyMap
from Ortho import ChordMap
from Ortho import Usbkb
from Ortho import Orthokb
from Ortho import StateControl as SC
from HidUsage import USBKB as KB
from HidUsage import USBKP as KP
from HidUsage import USBCO
import adafruit_led_animation.color as C

PKEYS = 4 # The number of special keys in the LKEY and RKEY sets (many tuples below must have this number of elements)

# s1 is used in boot.py to control presentation of CIRCUITPY and serial console
s1 = digitalio.DigitalInOut(board.A0)
s1.pull = digitalio.Pull.UP
debug = 1 if not s1.value else 0

# s2 is used to control US or Non-US key interpretation
s2 = digitalio.DigitalInOut(board.A1)
s2.pull = digitalio.Pull.UP
# s3 is used to control USB standard or Apple implementations of GRAVE, ¬, \ and | codes.
s3 = digitalio.DigitalInOut(board.D6)
s3.pull = digitalio.Pull.UP

CO = USBCO(us=s2.value, apple=s3.value)

s4 = digitalio.DigitalInOut(board.D9)
s4.pull = digitalio.Pull.UP


class KEY_MAPS:
    ''' Never instanced, this class is a container for constants defining the hardware layout. Must Contain:
        ROWPINS: Tuple of the GPIO pins used as row sense lines in the keyswitch matrix.
        COLPINS: Tuple of the GPIO pins used as column drive lines in the keyswitch matrix.
        KEY2MAP: IMap with one integer per keyswitch. Index is physical key number, value is logical top left to bottom right.
        MKEYMAP: IMap with one integer per keyswitch. Index is logical key number, value is 0 for TKEY
                 1..PKEYS for LKEY, -1..-PKEYS for RKEY.
        NEOPIXEL: Single GPIO pin used to drive the Neopixel chain.
        PIXBRIGHT: Float 0..1 representing the base brightness of the NeoPixels.
        MAP2PIX: Tuple containing a tuple per row with each having an integer element, the NeoPixel address, per column.
    '''

    ROWPINS = (board.D25, board.D24, board.A3, board.A2, board.D10, board.D11, board.D12, board.D13)

    COLPINS = (board.SCK, board.MOSI, board.MISO, board.RX, board.TX, board.D4)

    KEY2MAP = IMap(
        (
            47,46,45,44,43,42,35,34,33,32,31,30, #00-06-11
            23,22,21,20,19,18,11,10, 9, 8, 7, 6, #12-18-23
            41,40,39,38,37,36,29,28,27,26,25,24, #24-30-35
            17,16,15,14,13,12, 5, 4, 3, 2, 1, 0  #36-42-47
        )
    )

    MKEYMAP = IMap(
        (
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1,
            2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2,
            3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3,
            4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4
        )
    )

    NEOPIXEL = board.D5

    PIXBRIGHT = 0.3

    MAP2PIX = (
        ( 36,37,38,39,40,41,42,43,44,45,46,47 ),
        ( 35,34,33,32,31,30,29,28,27,26,25,24 ),
        ( 12,13,14,15,16,17,18,19,20,21,22,23 ),
        ( 11,10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 )
    )


class CODE_MAPS:
    ''' Never instanced, this class is a container for constants defining the keyboard to USB HID mappings. May Contain:
        KeyMap instances: The entries can be USB constants from the KB (keyboard) or KP (keypad) classes, tuples of up to
            six such constances (keys to be down simultaneously), constants from an instance of the USBCO class named CO
            which containes named multi-key tuples tailored for either US or Non-US keyboard settings, and Enum values
            from the SC class which supply state switches processed internally to the keyboard, or strings.
        CodeMap: These are KeyMap instances indexed by character codes in strings. If another KeyMap instance contains
            strings, it must have a code_map parameter specified to supplu the USB keycodes for each possible character.
        KeyMap: These are KeyMap instances indexed by logical key number. They contain the USB actions triggered by each
            typing key. These maps are activated by chords of the multifunction keys and are referenced in the CHORDS
            map. They may also be used as base maps for overlays and specified in the base_map parameter. Any entry in
            the overlay map which is not indexed or has the value None will delegate through to the base_map recursively.
        CHORDS (required singleton instance of ChordMap): One entry per binary combination of PKEY (therefore 2**PKEYS
            entries). Values must be None, a KeyMap instance or a Tuple of KeyMap instance and a Colour tuple.
        PTAP (required KeyMap instance with one entry per PKEY): Actions when a single PKEY is tapped, possibly with a
            chord of SKEY modifiers, after SC.CML.
        UTAP (required KeyMap instance with one entry per PKEY): Actions when a single PKEY is tapped after a chord of
            SKEY modifiers, after SC.CMU. Typically would also be assigned to the shift key entry in SFUNC.
        LMOD (required KeyMap instance with one entry per PKEY): Wrapping actions when a PKEY is held down and TKEY or
            SKEY is/are tapped. These codes are typically the modifiers Shift, Cntrl, Alt and Gui when PKEY = LKEY.
        RMOD (required KeyMap instance with one entry per PKEY): Ditto LMOD, but when PKEY = RKEY.
        SFUNCS (required IMap instance with one entry per PKEY): Contains a KeyMap for each single PKEY held down while
            SKEY are tapped. Each KeyMap contains one entry for each SKEY. The SC.CMU and/or SC.CML actions, if assigned,
            must be assigned in these KeyMaps and normally would be assigned to all entries in the KeyMap.
        CFUNC (required KeyMap instance with one entry per PKEY): Actions when a chord of PKEY is held down and SKEY
            are tapped. SC.MLK would normally be assigned to one of these keys to lock in a map selection.
    '''

    CODE_TABLE_UK = KeyMap(
        ( # CodeMap for UK ASCII
            KB.ENT, ) + (None,)*18 + (
            KB.SP, CO.EXCM, CO.DQOT, CO.HASH, CO.DOLR, CO.PCNT, CO.AMPS, KB.QUOTE,
            CO.OBKT, CO.CBKT, CO.STAR, CO.PLUS, KB.COMMA, KB.MINUS, KB.FSTOP, KB.FSLSH,
            KB.D0, KB.D1, KB.D2, KB.D3, KB.D4, KB.D5, KB.D6, KB.D7, KB.D8, KB.D9,
            CO.COLON, KB.SEMIC, CO.OANG, KB.EQ, CO.CANG, CO.QMK, CO.AT,
            (KB.LSFT, KB.A), (KB.LSFT, KB.B), (KB.LSFT, KB.C), (KB.LSFT, KB.D), (KB.LSFT, KB.E), (KB.LSFT, KB.F), (KB.LSFT, KB.G),
            (KB.LSFT, KB.H), (KB.LSFT, KB.I), (KB.LSFT, KB.J), (KB.LSFT, KB.K), (KB.LSFT, KB.L), (KB.LSFT, KB.M), (KB.LSFT, KB.N),
            (KB.LSFT, KB.O), (KB.LSFT, KB.P), (KB.LSFT, KB.Q), (KB.LSFT, KB.R), (KB.LSFT, KB.S), (KB.LSFT, KB.T), (KB.LSFT, KB.U),
            (KB.LSFT, KB.V), (KB.LSFT, KB.W), (KB.LSFT, KB.X), (KB.LSFT, KB.Y), (KB.LSFT, KB.Z),
            KB.OBRCE, CO.BSLSH, KB.CBRCE, CO.CRT, CO.USCORE, CO.GRAVE,
            KB.A, KB.B, KB.C, KB.D, KB.E, KB.F, KB.G, KB.H, KB.I, KB.J, KB.K, KB.L, KB.M, KB.N, KB.O,
            KB.P, KB.Q, KB.R, KB.S, KB.T, KB.U, KB.V, KB.W, KB.X, KB.Y, KB.Z,
            CO.OCURL, CO.PIPE, CO.CCURL, CO.TILD
        ),
        first_index = 13
    )

    KEY_MAP_QWERTY = KeyMap(
        ( # KeyMap for basic QWERTY alpha-numeric layer.
            None, KB.D1, KB.D2, KB.D3, KB.D4, KB.D5, KB.D6, KB.D7, KB.D8, KB.D9, KB.D0, None,
            None, KB.Q, KB.W, KB.E, KB.R, KB.T, KB.Y, KB.U, KB.I, KB.O, KB.P, None,
            None, KB.A, KB.S, KB.D, KB.F, KB.G, KB.H, KB.J, KB.K, KB.L, KB.SEMIC, None,
            None, KB.QUOTE, KB.Z, KB.X, KB.C, KB.V, KB.B, KB.N, KB.M, KB.COMMA, KB.FSTOP, None
        )
    )

    KEY_MAP_EXTENDED = KeyMap(
        ( # KeyMap for overflow layer with function keys and extra punctuation.
            None, KB.F1, KB.F2, KB.F3, KB.F4, KB.F5, KB.F6, KB.F7, KB.F8, KB.F9, KB.F10, None,
            None, CO.QMK, KB.UP, CO.HASH, KB.PGUP, KB.HOME, CO.NOTS, CO.PLUS, KB.MINUS, KB.OBRCE, KB.CBRCE, None,
            None, KB.LEFT, KB.DOWN, KB.RIGHT, KB.PGDN, KB.END, CO.GRAVE, CO.TILD, KB.EQ, CO.OCURL, CO.CCURL, None,
            None, KB.F11, KB.F12, KB.F13, KB.F14, KB.F15, KB.F16, CO.PIPE, CO.USCORE, KB.FSLSH, CO.BSLSH, None
        )
    )

    KEY_MAP_TEST = KeyMap(
        ( # Test overlay KeyMap with a string.
            "John Hind\r",
        ),
        base_map = KEY_MAP_QWERTY,
        code_map = CODE_TABLE_UK,
        first_index = 1
    )

    CHORDS = ChordMap(
        (
            None,     # Chord 0000 (CANNOT BE ACCESSED)
            None,     # Chord 0001 (ONLY ACCESSED AFTER TWO KEY CHORD)
            None,     # Chord 0010 (ONLY ACCESSED AFTER TWO KEY CHORD)
            (KEY_MAP_TEST, C.GREEN),    # Chord 0011
            None,     # Chord 0100
            None,     # Chord 0101
            (KEY_MAP_EXTENDED, C.RED),  # Chord 0110
            None,     # Chord 0111
            None,     # Chord 1000 (ONLY ACCESSED AFTER TWO KEY CHORD)
            None,     # Chord 1001
            None,     # Chord 1010
            None,     # Chord 1011
            (KEY_MAP_QWERTY, C.BLACK),  # Chord 1100
            None,     # Chord 1101
            None,     # Chord 1110
            None      # Chord 1111
        ),
        pkeys = PKEYS,
        initial = 0b1100
    )

    PTAP = KeyMap(
        (
            KB.BS,
            KB.TAB,
            KB.ENT,
            KB.SP
        )
    )

    UTAP = KeyMap(
        (
            KB.DEL,
            KB.INS,
            KB.ESC,
            KB.CPLK
        )
    )
    LMOD = KeyMap(
        (
            KB.LGUI,
            KB.LALT,
            KB.LCTL,
            KB.LSFT
        )
    )

    RMOD = KeyMap(
        (
            KB.RGUI,
            KB.RALT,
            KB.RCTL,
            KB.RSFT
        )
    )

    SFUNCS = IMap(
        (
            KeyMap((KB.UP, KB.RIGHT, KB.LEFT, KB.DOWN)),
            KeyMap((SC.CMU,)*PKEYS),
            KeyMap((SC.CML,)*PKEYS),
            UTAP
        )
    )

    CFUNC = KeyMap(
        (
            KB.DEL,
            KB.INS,
            KB.ESC,
            SC.MLK
        )
    )

def update_leds(self, leds):
    kb.pixels.indexing()
    kb.pixels[(37,46)] = C.BLUE if leds[leds.CAPS_LOCK] else C.BLACK
    kb.pixels.show()

Usbkb.notifier = update_leds

def update_chords(newchord, colour):
    kb.pixels.indexing(index_mode=PixelMap.COLUMNS)
    kb.pixels[(0,11)] = C.BLACK
    kb.pixels.indexing(index_mode=PixelMap.RASTER)
    if colour != C.BLACK:
        px = []
        if newchord[0]: px.extend((0, 11))
        if newchord[1]: px.extend((12, 23))
        if newchord[2]: px.extend((24, 35))
        if newchord[3]: px.extend((36, 47))
        kb.pixels[px] = colour
    kb.pixels.show()

CODE_MAPS.CHORDS.notifier = update_chords

time.sleep(2)  # Sleep for a bit to avoid a race condition on some systems

usb = Usbkb(CODE_MAPS, debug)
kb = Orthokb(usb, KEY_MAPS, debug)
while True:
    kb.update()
    usb.update()