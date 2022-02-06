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

devices = []

print("Discovery done")
try:
    for device in xled.discover.xdiscover(timeout=2):
        devices.append(device)
except xled.exceptions.DiscoverTimeout as e:
    pass

print(devices)

controls = list(map(lambda d: deviceToController(d), devices))

control = controls[1]
#print(control.get_mode().data)
#print(control.get_led_movie_config().data)



layout = control.get_led_layout().data
coords = layout['coordinates']
num_leds = len(coords)
print(f'We have {len(coords)} leds')

def flatten(inlist):
    return [a for tup in inlist for a in tup]

def randomImg():
    def randomValue():
        return numpy.random.randint(0, 255)

    def randomPixel():
        return randomValue(), randomValue(), randomValue()


    img = [randomPixel() for lamp in range(num_leds)]

    return flatten(img)

def normalizedFloatToInt8(float_val):
    return round(float_val * 255)

def renormalize(coord):
    return (coord +1)/2

def inputImg(input_op):
    out = []
    for coord in coords:
        colours = input_op.sample(
            u=renormalize(coord['x']), v=coord['y'])
        
        [r, g, b, a] = list(map(lambda c: normalizedFloatToInt8(c), colours))
        out.append([r,g,b])

    #print(out)
    return flatten(out)

def getImg(input_op):
    return inputImg(input_op)

control.set_mode("rt")




#control.set_led_effects_current(effects["unique_ids"][2])
#control.set_led_effects_current(0)


#controls[0].set_brightness(100)
#controls[1].set_brightness(100)

pars = None
def onSetupParameters(scriptOp):

    #TODO: UI for device selection
    #page = scriptOp.appendCustomPage('Twinkly')
    #pars = page.appendStrMenu("Device", label="device")
    #print(pars[0].expr)

    

    return

# called whenever custom pulse parameter is pushed


def onPulse(par):
    return


def onCook(scriptOp):
    #a = numpy.random.randint(0, high=255, size=(2, 2, 4), dtype='uint8')
    #scriptOp.copyNumpyArray(a)
    
    #.sample(x=0,y=0)

    frame = io.BytesIO(bytes(getImg(scriptOp.inputs[0])))
    control.set_rt_frame_socket(frame, 3)

    return
