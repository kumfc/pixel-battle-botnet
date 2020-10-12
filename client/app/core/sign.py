import struct
import js2py as js
import app.utils.logger as log
from app import config


def get_sign(pw):
    window = "var window = {WebSocket: 1, parseInt: parseInt, Math: Math};"
    document = "document = {createElement: function(e){ return ({tagName: e.toUpperCase()}) }}; setTimeout = function(a, b){ return; };" 
    res = js.eval_js(document + window + pw)
    return res


def prepare_pixel_packet(x, y, color, flag = 0):
    e = {'color': color, 'flag': flag, 'x': x, 'y': y}
    packet = convert(e)
    if config.drawlog:
        log.info(f'Painting {[x, y, color]}, sign {struct.pack("<L", packet)}')
    return struct.pack('<L', packet)


def convert(e):
    t = e['color'] + e['flag'] * 25
    return e['x'] + e['y'] * config.max_width + config.field_size * t
