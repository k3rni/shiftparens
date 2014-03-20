import xdotool, uinput, nop, xtest

EMITTERS = {
    'xdo': xdotool.XdotoolEmitter,
    'xtest': xtest.XTestEmitter,
    'uinput': uinput.UInputEmitter,
    'nop': nop.NopEmitter
}
