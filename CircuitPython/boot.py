import board, digitalio
import storage, usb_cdc, usb_hid

s1 = digitalio.DigitalInOut(board.A0)
s1.pull = digitalio.Pull.UP

if s1.value:
    storage.disable_usb_drive()
    usb_cdc.disable()
    usb_hid.enable((Device.KEYBOARD), boot_device=1)
