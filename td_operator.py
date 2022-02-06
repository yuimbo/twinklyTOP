# me - this DAT
# scriptOp - the OP which is cooking
import sys
mypath = "/Users/jimmyghaderi/.pyenv/versions/3.7.12/lib/python3.7/site-packages"
if mypath not in sys.path:
    sys.path.append(mypath)


import xled
import numpy
import io

def deviceToController(device):
    return xled.ControlInterface(
        device.ip_address, device.hw_address)

def deviceNames(device):
    return device.id

devices = []

try:
    for device in xled.discover.xdiscover(timeout=2):
        devices.append(device)
except xled.exceptions.DiscoverTimeout as e:
    pass


devices = sorted(devices, key = lambda d: d.id)
controls = list(map(lambda d: deviceToController(d), devices))
for control in controls:
    control.set_mode("rt")
layouts = list(map(lambda c: c.get_led_layout().data, controls))



def flatten(inlist):
    return [a for tup in inlist for a in tup]

def normalizedFloatToInt8(float_val):
    return round(float_val * 255)

def renormalize(coord):
    return (coord +1)/2

def makeImg(input_op, coords):
    out = []
    for coord in coords:
        colours = input_op.sample(
            u=renormalize(coord['x']), v=coord['y'])
        
        [r, g, b, a] = list(map(lambda c: normalizedFloatToInt8(c), colours))
        out.append([r,g,b])
        #TODO: Detect & handle RGBW

    return flatten(out)

device_par = None
previous_device_par = None

def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Twinkly')
    [device_par] = page.appendMenu("Device")

    device_par.menuNames = list(range(len(devices)))
    device_par.menuLabels = list(map(lambda d: deviceNames(d), devices))

    return


def onPulse(par):
    return


def onCook(scriptOp):
    current_id = scriptOp.pars("Device")[0]
    control = controls[current_id]

    layout = layouts[current_id]
    coords = layout['coordinates']
    

    frame = io.BytesIO(bytes(makeImg(scriptOp.inputs[0], coords)))

    #TODO: Handle closing previous socket when changing device
    control.set_rt_frame_socket(frame, 3)

    return
