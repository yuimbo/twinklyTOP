# me - this DAT
# scriptOp - the OP which is cooking
import sys
#https://docs.derivative.ca/Category:Python#Installing_Custom_Python_Packages
modules_path = "/Users/jimmyghaderi/.pyenv/versions/3.7.12/lib/python3.7/site-packages"
if modules_path not in sys.path:
    sys.path.append(modules_path)

import xled
import numpy
import threading
import io

def deviceToController(device):
    return xled.ControlInterface(
        device.ip_address, device.hw_address)

def deviceNames(device):
    return device.id

def discoverDevices():
    devices = []
    try:
        for device in xled.discover.xdiscover(timeout=2):
            devices.append(device)
    except xled.exceptions.DiscoverTimeout as e:
        pass
    return sorted(devices, key=lambda d: d.id)

devices = discoverDevices()
controls = list(map(lambda d: deviceToController(d), devices))
for control in controls:
    control.set_mode("rt")
layouts = list(map(lambda c: c.get_led_layout().data, controls))
device_infos = list(map(lambda c: c.get_device_info().data, controls))

def flatten(inlist):
    return [a for tup in inlist for a in tup]

def normalizedFloatToInt8(float_val):
    return round(float_val * 255)

def renormalize(coord):
    return (coord + 1) / 2

def remapImg(image, coords, rgbw=False):
    out = []
    [h, w] = image.shape
    for coord in coords:
        channels = image[
            round(renormalize(coord['y'] * h)), 
            round(renormalize(coord['x'] * w))]
        [r, g, b, a] = list(map(lambda c: normalizedFloatToInt8(c), channels))
        if rgbw:
            w = (min([r,g,b]))
            [r,g,b] = [c - w for c in [r,g,b]]
            channels = [w, r, g, b]
        else:
            channels = [r,g,b]
        out.append([c * 255 for c in channels])
    return flatten(out)


def sendImage(control, coords, image, rgbw=False):
    frame = io.BytesIO(bytes(
        remapImg(image, coords, rgbw)))
    #TODO: Handle closing previous socket when changing device
    control.set_rt_frame_socket(frame, 3)

def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Twinkly')
    [device_par] = page.appendMenu("Device")
    device_par.menuNames = list(range(len(devices)))
    device_par.menuLabels = [d.id for d in devices]
    return

t = threading.Thread()
def onCook(scriptOp):
    current_id = scriptOp.pars("Device")[0]
    control = controls[current_id]
    coords = layouts[current_id]['coordinates']
    if not t.is_alive():
        t = threading.Thread(
            target=sendImage, 
            daemon=True,
            args=(
                control,
                coords,
                scriptOp.inputs[0].numpyArray(),
                device_infos[current_id]['led_profile'] == 'RGBW'),
            )
        t.start()
    return
