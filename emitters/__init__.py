import xdotool, uinput, nop

EMITTERS = {
    'xdo': xdotool.XdotoolEmitter,
    'uinput': uinput.UInputEmitter,
    'nop': nop.NopEmitter
}
