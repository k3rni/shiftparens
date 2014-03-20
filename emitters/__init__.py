import xdotool, uinput, nop, xtest, vim

EMITTERS = {
    'xdo': xdotool.XdotoolEmitter,
    'xtest': xtest.XTestEmitter,
    'uinput': uinput.UInputEmitter,
    'vim': vim.VimEmitter,
    'nop': nop.NopEmitter
}
