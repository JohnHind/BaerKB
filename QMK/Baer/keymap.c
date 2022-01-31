#include QMK_KEYBOARD_H
#include <print.h>

/* Copyright 2020 John Hind
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

// Multi-purpose control keys (MKEY). Two groups of keys are reserved as MKEY set. These are typically the
// right-most (RKEY) and left-most (LKEY) columns and each subset may contain up to eight keys. The two
// subsets are interchangable with the first used being designated 'primary' (PKEY) and the other
// 'secondary' (SKEY). The keys that are not in the MKEY set are designated 'typing' (TKEY).
// The following actions may be used to generate independently specified keycodes:
// 1. Tap a PKEY. Typically generates a non-typing keycode such as space, return, escape etc.
// 2. Hold a PKEY while tapping TKEY. Typically applies a modifier to the TKEY.
// 3. Hold a PKEY while tapping SKEY. Typically accesses further non-typing keycodes.
// 4. Hold a chord of two or more PKEY while tapping TKEY. Typically selects an overlay for the TKEY.
// 5. Hold a chord of PKEY whilst tapping SKEY. Typically acts on an overlay, for example locking it.
// 6. Hold a PKEY, hold one or more SKEY, optionally release the PKEY. Typically applies single or 
//    multiple modifiers. TKEY may be tapped whilst holding down the SKEY chord.
// 7. Hold a PKEY, hold one or more SKEY, release the PKEY, tap a PKEY. Typically applies single or
//    multiple modifiers to a non-typing keycode (for example ctrl+alt+del).

// CONFIGURATION CONSTANTS //

#define MK_MKEYS (4)		// The number of keys in each set LKEY or RKEY (2 - 8)

enum mk_keycodes {
	MK_LKEY1 = SAFE_RANGE,	// Left-side Multi Keys
	MK_LKEY2, MK_LKEY3, MK_LKEY4, MK_LKEY5, MK_LKEY6, MK_LKEY7,
	MK_LKEY8,				// ------

	MK_RKEY1,				// Right-side Multi Keys
	MK_RKEY2, MK_RKEY3, MK_RKEY4, MK_RKEY5, MK_RKEY6, MK_RKEY7,
	MK_RKEY8,				// ------

	MK_LLOCK,				// Lock the layer selected by PKEY chord
	MK_NUMT,				// KC_NLCK if NUMLOCK off, else ignored
	MK_NUMF,				// KC_NLCK if NUMLOCK on, else ignored
	MK_SFT,					// KC_LSFT if LKEY, else KC_RSFT
	MK_CTRL,				// KC_LCTRL if LKEY, else KC_RCTRL
	MK_ALT,					// KC_LALT if LKEY, else KC_RALT
	MK_GUI					// KC_LGUI if LKEY, else KC_RGUI
};

#define NON_US				// Comment this out if building for US layout

#ifdef NON_US				// Neutral keycodes for punctuation keys that differ between US and non-US layouts
#define NC_HASH KC_NUHS			// # (Hash)
#define NC_TILD S(KC_NUHS)		// ~ (Tild)
#define NC_BKSL KC_NUBS			// (Backslash)
#define NC_PIPE S(KC_NUBS)		// | (Pipe)
#define NC_SQOT KC_QUOT			// ' (Single Quote)
#define NC_DQOT S(KC_2)			// " (Double Quote)
#define NC_NOT  S(KC_GRV)       // ¬ (Located where Tild is on US  keyboard)
#else
#define NC_HASH S(KC_3)			// # (Hash)
#define NC_TILD S(KC_GRV)		// ~ (Tild)
#define NC_BKSL KC_BSLS			// (Backslash)
#define NC_PIPE S(KC_BSLS)		// | (Pipe)
#define NC_SQOT KC_QUOT			// ' (Single Quote)
#define NC_DQOT S(KC_QUOT)		// " (Double Quote)
#endif

// Standard QMK keymap can use standard keycodes or the above. Include Multi key codes on base layer and KC_TRNS at
// those positions on all overlay layers:
enum mk_layers {
  _BASE,		// This layer is always active and defines the LKEY and RKEY sets
  _QWERTY,		// This is the default overlay which defines the TKEY set
  _OVERFLOW,	// This is the first overlay which defines the TKEY overflow and control set
  _NUMPAD,		// This is the second overlay which defines the TKEY set as a numeric keypad
  // _LAYER_NAME, // Insert additional layers names here
  MK_KEYMAPS	// Guard value sets the number of layers that are defined
};
// Keycode sent on activating an overlay layer. Must be one element per keymap:
const uint16_t PROGMEM mk_kclin[MK_KEYMAPS] =
	{KC_NO, KC_NO, KC_NO, MK_NUMT};

const uint16_t PROGMEM keymaps[MK_KEYMAPS][MATRIX_ROWS][MATRIX_COLS] = {
	[_BASE] = LAYOUT_planck_grid(
		MK_LKEY4,KC_NO, KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	MK_RKEY4, 
		MK_LKEY3,KC_NO, KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	MK_RKEY3, 
		MK_LKEY2,KC_NO, KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO,  MK_RKEY2, 
		MK_LKEY1,KC_NO, KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO, 	KC_NO,  KC_NO,  KC_NO,	MK_RKEY1),
	[_QWERTY] = LAYOUT_planck_grid(
		KC_TRNS,KC_1, 	KC_2, 	KC_3, 	KC_4, 	KC_5, 	KC_6, 	KC_7, 	KC_8, 	KC_9, 	KC_0, 	KC_TRNS, 
		KC_TRNS,KC_Q, 	KC_W, 	KC_E, 	KC_R, 	KC_T, 	KC_Y, 	KC_U, 	KC_I, 	KC_O, 	KC_P, 	KC_TRNS, 
		KC_TRNS,KC_A, 	KC_S, 	KC_D, 	KC_F, 	KC_G, 	KC_H, 	KC_J, 	KC_K, 	KC_L, 	KC_SCLN,KC_TRNS, 
		KC_TRNS,KC_QUOT,KC_Z, 	KC_X, 	KC_C, 	KC_V, 	KC_B, 	KC_N, 	KC_M,	KC_COMM,KC_DOT,	KC_TRNS),
	[_OVERFLOW] = LAYOUT_planck_grid(
		KC_TRNS,KC_F1,	KC_F2, 	KC_F3,	KC_F4,	KC_F5,	KC_F6,	KC_F7,	KC_F8,	KC_F9,	KC_F10,	KC_TRNS, 
		KC_TRNS,KC_QUES,KC_UP, 	NC_HASH,KC_PGUP,KC_HOME,NC_NOT,	KC_PLUS,KC_MINS,KC_LBRC,KC_RBRC,KC_TRNS, 
		KC_TRNS,KC_LEFT,KC_DOWN,KC_RGHT,KC_PGDN,KC_END,	KC_GRV,	NC_TILD,KC_EQL,	KC_LCBR,KC_RCBR,KC_TRNS, 
		KC_TRNS,KC_F11,	KC_F12,	KC_F13,	KC_F14,	KC_F15,	KC_F16,	NC_PIPE,KC_UNDS,KC_SLSH,NC_BKSL,KC_TRNS),
	[_NUMPAD] = LAYOUT_planck_grid(
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_CALC,KC_P7,	KC_P8,	KC_P9,	KC_PSLS,KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_P4,	KC_P5,	KC_P6,	KC_PAST,KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_PEQL,KC_P1,	KC_P2,	KC_P3,	KC_PMNS,KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_PCMM,KC_P0,	KC_PDOT,KC_PENT,KC_PPLS,KC_TRNS)
/*
	// Template for defining additional layers:
	[_ LAYER_NAME] = LAYOUT_planck_grid(
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_TRNS, 
		KC_TRNS,KC_NO,	KC_NO, 	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_NO,	KC_TRNS)
*/
};
// Keycode sent on deactivating an overlay layer. Must be one element per keymap:
const uint16_t PROGMEM mk_kclout[MK_KEYMAPS] =
	{KC_NO, KC_NO, KC_NO, KC_NO};
// There is an entry for every combination of PKEY specifying a layer number. Only the combinations
// of at least two keys may be set to a layer. Other combinations and any unused must be 0:
const uint8_t  PROGMEM mk_lyr[(1<<MK_MKEYS)] = {
	0, 0, 0,	// !!! 0000, 0001, 0010 <2 keys not valid: leave 0 !!!
	_QWERTY,			// 0011
	0,			// !!! 0100 <2 keys not valid: leave 0 !!!
	0,					// 0101
	_OVERFLOW,			// 0110
	0,	 				// 0111
	0,			// !!! 1000 <2 keys not valid: leave 0 !!!
	0, 					// 1001
	0, 					// 1010
	0,					// 1011
	_NUMPAD,			// 1100
	0, 					// 1101
	0,					// 1110
	0					// 1111
};
// The initial overlay layer on startup:
#define INIT_OVERLAY _QWERTY

// One of these keys is tapped when a single PKEY is released without pressing any other key:
const uint16_t PROGMEM mk_kc1[MK_MKEYS] =
	{KC_SPC,  	KC_ENTER, 	KC_TAB,  	KC_BSPC};
// One of these keys is registered before a TKEY when a single PKEY is held down as the TKEY
// is pressed. They are unregistered when the PKEY is released:
const uint16_t PROGMEM mk_kc2[MK_MKEYS] =
	{MK_SFT, 	MK_CTRL, 	MK_ALT, 	MK_GUI};
// There is one row per PKEY with a column for each SKEY. When a single PKEY is
// held down and a SKEY is pressed the following code is sent. The PKEY is 'sticky' so
// it may be released while one or more SKEY is held down:
const uint16_t PROGMEM mk_kc3[MK_MKEYS][MK_MKEYS] = {
	{KC_CLCK,	KC_ESC,		KC_INS, 	KC_DEL},	// Shifted functions of SKEYs
	{MK_SFT,	MK_CTRL, 	MK_ALT, 	MK_GUI},	// 2nd PKEY makes SKEYs modifiers
	{MK_SFT,	MK_CTRL,	MK_ALT, 	MK_GUI},	// 3rd PKEY makes SKEYs modifiers
	{KC_DOWN,	KC_LEFT,	KC_RIGHT, 	KC_UP}		// Arrow functions of SKEYs
};
// When a chord of two or more PKEY are held down and SKEY is pressed the following code is sent:
const uint16_t PROGMEM mk_kc5[MK_MKEYS] =
	{MK_LLOCK,	KC_NO,  	KC_NO,  	KC_NO};
// There is one row per 'sticky' PKEY (see above) and one column for each PKEY pressed after the
// initial keypress is released.
const uint16_t PROGMEM mk_kc7[MK_MKEYS][MK_MKEYS] = {
	{KC_NO,		KC_NO,		KC_NO, 		KC_NO},
	{KC_SPC,	KC_ENTER, 	KC_TAB, 	KC_BSPC},	// modifiers apply to unshifted PKEY functions
	{KC_CLCK,	KC_ESC,	    KC_INS, 	KC_DEL},	// modifiers apply to shifted PKEY functions
	{KC_NO,		KC_NO,		KC_NO, 		KC_NO}
};

// END OF CONFIGURATION CONSTANTS //


uint8_t  mk_state;	// LS 2 bits are the primary side; remaining 6 bits are the mode; whole is 0 when no MKEY down.
#define LEFT (1)
#define RIGHT (2)
uint8_t mk_pside(void) {return (mk_state & 3u);}
uint8_t mk_sside(void) {switch (mk_pside()) {case RIGHT: return LEFT; case LEFT: return RIGHT; default: return 0;};}
#define MODE0 (0)	// All MKEY released
#define MODE1 (4u)	// A single PKEY pressed - PKEY, SKEY assigned if released immediately, primary function.
#define MODE2 (8u)	// A TKEY was pressed with a single PKEY held down - simple modifier mode
#define MODE3 (12u)	// A SKEY was pressed with a single PKEY held down - modified SKEY function
#define MODE4 (16u)	// From MODE1, an additional PKEY pressed - chord mode, sets a TKEY layer
#define MODE5 (20u)	// With a PKEY chord held down, SKEY pressed - layer functions (eg Lock)
#define MODE6 (24u)	// From MODE3, PKEY released - no action, just enables entry to ...
#define MODE7 (28u) // Additional ssignments on PKEY nested in chords of SKEY modifiers
uint8_t mk_mode(void) {return (mk_state & 252u);}
// Use left or right modifier key codes:
uint8_t mk_mside(void) {switch (mk_mode()) {case MODE3: case MODE6: case MODE7: return mk_sside(); default: return mk_pside();};}
void    mk_setmode(uint8_t md) {
	//dprintf("mk_setmode: MODE%u -> MODE%u \n", mk_mode()>>2, md>>2);
	mk_state = (mk_state & 3u) | md;
}

uint8_t  mk_pkeys;	// Bit-map of PKEY currently pressed
uint8_t  mk_skeys;	// Bit-map of SKEY currently pressed
// True iff bit index n (0..7) is the only bit set in v:
bool mk_issolebit(uint8_t n, uint8_t v) { return ((1u << n) == v); }
// Bit index (0..7) of the sole active bit set in v, or 0xFF:
uint8_t mk_solebit(uint8_t v) { if (v != 0) for (int i=0; (i < MK_MKEYS); i++) if (mk_issolebit(i, v)) return i; return 0xFF; }
// True iff bit index n (0..7) is set in v:
bool mk_isbit(uint8_t n, uint8_t v) { return (((1u << n) & v) != 0); }
// Set the bit index n (0..7) in byte at address a:
void mk_setbit(uint8_t n, uint8_t* a) { *a |= (1u << n); }
// Clear the bit index n (0..7) in byte at address a:
void mk_clearbit(uint8_t n, uint8_t* a) { *a &= !(1u << n); }
// True iff v has no bits set:
bool mk_isnone(uint8_t v) { return (v == 0); }
// True iff v has all active bits set:
bool mk_isall(uint8_t v) { return (v == ((1u<<MK_MKEYS)-1));}

uint8_t  mk_ix;	    // Saved index of PKEY
uint8_t  mk_layer;  // The currently active TKEY layer
uint8_t  mk_blay;   // The current base TKEY layer

// Act on keydown for our code or register standard code:
void mk_regkc(uint16_t kc) {
	//dprintf("mk_regkc: %u\n", kc);
	switch (kc) {
		case KC_NO:
			break;
		case MK_LLOCK:
			// Set the current layer as the base layer:
			mk_blay = mk_layer;
			break;
		case MK_NUMT:
			if ((host_keyboard_leds() & (1<<USB_LED_NUM_LOCK))==0) tap_code(KC_NLCK);
			break;
		case MK_NUMF:
			if ((host_keyboard_leds() & (1<<USB_LED_NUM_LOCK))!=0) tap_code(KC_NLCK);
			break;
		case MK_SFT:
			register_code((mk_mside() == LEFT)? KC_LSFT : KC_RSFT);
			break;
		case MK_CTRL:
			register_code((mk_mside() == LEFT)? KC_LCTRL : KC_RCTRL);
			break;
		case MK_ALT:
			register_code((mk_mside() == LEFT)? KC_LALT : KC_RALT);
			break;
		case MK_GUI:
			register_code((mk_mside() == LEFT)? KC_LGUI : KC_RGUI);
			break;
		default:
			register_code(kc);
			break;
	}
}

// Act on keyup for our code or unregister standard code:
void mk_unregkc(uint16_t kc) {
	//dprintf("mk_unregkc: %u\n", kc);
	switch (kc) {
		case KC_NO:
		case MK_LLOCK:
		case MK_NUMT:
		case MK_NUMF:
			break;
		case MK_SFT:
			unregister_code((mk_mside() == LEFT)? KC_LSFT : KC_RSFT);
			break;
		case MK_CTRL:
			unregister_code((mk_mside() == LEFT)? KC_LCTRL : KC_RCTRL);
			break;
		case MK_ALT:
			unregister_code((mk_mside() == LEFT)? KC_LALT : KC_RALT);
			break;
		case MK_GUI:
			unregister_code((mk_mside() == LEFT)? KC_LGUI : KC_RGUI);
			break;
		default:
			unregister_code(kc);
			break;
	}
}

// Tap (register then immediately unregister) a keycode:
void mk_tapkc(uint16_t kc) {
	mk_regkc(kc);
	mk_unregkc(kc);
}

// Select a TKEY overlay:
void mk_setlayer(uint8_t lr) {
	//dprintf("mk setlayer: %u %u\n", lr, mk_layer);
	if (lr == 0) return;
	if (lr != mk_layer) {
		mk_tapkc(mk_kclout[mk_layer]);
		layer_off(mk_layer);
		layer_on(lr);
		mk_tapkc(mk_kclin[lr]);
	}
	mk_layer = lr;
}

// Act when multi key 'ix' pressed on 'side':
bool mk_mkeyp(uint8_t ix, uint8_t side) {
	// If PKEY not assigned, assign to this side:
	if (mk_state == 0) mk_state = side;
	if (side == mk_pside()) {
		if (!mk_isbit(ix, mk_pkeys)) {
			// Press PKEY : Set flag in PKEY set:
			mk_setbit(ix, &mk_pkeys);
			switch (mk_mode()) {
				case 0:
					// First PKEY:
					mk_setmode(MODE1);
					mk_ix = ix;
					break;
				case MODE1:
					// PKEY Chord:
					mk_setmode(MODE4);
					mk_setlayer(mk_lyr[mk_pkeys]);
					break;
				case MODE6:
					// Second press of PKEY after release with SKEY held:
					mk_setmode(MODE7);
					mk_regkc(mk_kc7[mk_ix][ix]);
					break;
				default:
					break;
			}
		}
	} else {
		if (!mk_isbit(ix, mk_skeys)) {
			// Press SKEY : Set flag in SKEY set:
			mk_setbit(ix, &mk_skeys);
			switch(mk_mode())	{
				case MODE1:
					mk_setmode(MODE3);
				case MODE3:
				case MODE6:
				case MODE7:
					mk_regkc(mk_kc3[mk_ix][ix]);
					break;
				case MODE4:
				case MODE5:
					mk_setmode(MODE5);
					mk_regkc(mk_kc5[ix]);
					break;
				default:
					break;
			}
		}
	}
	return false;
}

// Act when multi key 'ix' released on 'side':
bool mk_mkeyr(uint8_t ix, uint8_t side) {
	if (side == mk_pside()) {
		// Release PKEY:
		switch(mk_mode()) {
			case MODE1:
				mk_tapkc(mk_kc1[ix]);
				break;
			case MODE2:
				mk_unregkc(mk_kc2[mk_ix]);
				break;
			case MODE3:
				mk_setmode(MODE6);
				break;
			case MODE7:
				mk_unregkc(mk_kc7[mk_ix][ix]);
			default:
				break;
		}
		// Clear flag in PKEY set:
		mk_clearbit(ix, &mk_pkeys);
	} else  {
		// Release SKEY:
		switch(mk_mode()) {
			case MODE3:
			case MODE6:
			case MODE7:
				mk_unregkc(mk_kc3[mk_ix][ix]);
				break;
			case MODE5:
				mk_unregkc(mk_kc5[ix]);
				break;
			default:
				break;
		}
		// Clear flag in SKEY set:
		mk_clearbit(ix, &mk_skeys);
	}
	if ((mk_pkeys == 0) && (mk_skeys == 0)) {
		// Revert any non-locked TKEY layer:
		mk_setlayer(mk_blay);
		//dprintf("mk_mkeyr: MODE%u -> MODE0\n", mk_mode()>>2);
		// Unassign PKEY:
		mk_state = 0;
		mk_ix = MK_MKEYS;
	}
	return false;
}

// Carry this out before processing a TKEY press:
bool mk_tkeyp(uint16_t kc) {
	if (mk_mode() == MODE1) {
		mk_setmode(MODE2);
		mk_regkc(mk_kc2[mk_ix]);
	}
	return true;
}

// Called by framework for every key press or release:
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
	//dprintf("PRU: %u %u %u \n", keycode, record->event.key.col, record->event.key.row);
	uint8_t ix;
	// Trap MKEY codes:
	if ((keycode >= MK_LKEY1) && (keycode <= MK_LKEY8)) {
		// An LKEY:
		ix = (uint8_t)(keycode - MK_LKEY1);
		if (record->event.pressed) {
			return mk_mkeyp(ix, LEFT);
		} else {
			return mk_mkeyr(ix, LEFT);
		}
	}
	if ((keycode >= MK_RKEY1) && (keycode <= MK_RKEY8)) {
		// An RKEY:
		ix = (uint8_t)(keycode - MK_RKEY1);
		if (record->event.pressed) {
			return mk_mkeyp(ix, RIGHT);
		} else {
			return mk_mkeyr(ix, RIGHT);
		}
	}
	if ((keycode > MK_RKEY8)){
		// One of our added keycodes if assigned in the main keymaps:
		if (record->event.pressed) {
			mk_regkc(keycode);
			return false;
		} else {
			mk_unregkc(keycode);
			return false;
		}
	}
	// Otherwise must be TKEY:
	if (record->event.pressed) return mk_tkeyp(keycode);
	return true;
}

// Called by framework on initialisation:
void keyboard_post_init_user(void) {
	//debug_enable=true;
	//debug_matrix=true;
	//debug_keyboard=true;
	//debug_mouse=true;
	mk_pkeys = 0;
	mk_skeys = 0;
	mk_state = 0;
	mk_ix = 0;
	mk_layer = 0;
	mk_blay = INIT_OVERLAY;
 	mk_setlayer(INIT_OVERLAY);
}