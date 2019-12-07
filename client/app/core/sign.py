import struct
import js2py as js
import core.logger as log


def get_sign(pw):
    window = "var window = {WebSocket: 1, parseInt: parseInt, Math: Math};"
    document = "document = {createElement: function(e){ return ({tagName: e.toUpperCase()}) }}; setTimeout = function(a, b){ return; };" 
    res = js.eval_js(document + window + pw)
    return res


def prepare_pixel_packet(x, y, color, flag = 0):
    e = {'color': color, 'flag': flag, 'x': x, 'y': y}
    packet = convert(e)
    log.info('Painting %s' % str([x, y, color]))
    return struct.pack('<L', packet)


def convert(e):
    t = e['color'] + e['flag'] * 25
    return e['x'] + e['y'] * 1590 + 636000 * t

