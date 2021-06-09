import cv2, colorsys, os, io, cmath, math, sys, webbrowser
import numpy as np
import time as t
import concurrent.futures as c
from scipy.interpolate import interp1d
import PySimpleGUI as sg 
import numba as nb
from PIL import Image

color_dict = {}
current_directory = os.getcwd() + "/Output"
fileName = 'bruh'

try:
    os.mkdir(current_directory)
except: 
    pass
 
# Mandelbrot Function 
@nb.njit([nb.types.Tuple((nb.u2, nb.f8))(nb.c16, nb.i8, nb.f8)])
def mandelbrot(c: complex, max_it: int, power: float) -> (int, float):
    z = c
    for i in range(max_it):
        if abs(z) > 2:
            return i, abs(z)
        z = z**power + c
    return 0, 0


# Burning Ship Function 
@nb.njit([nb.types.Tuple((nb.u2, nb.f8))(nb.c16, nb.i8, nb.f8)])
def burningShip(c: complex, max_it: int, power: float) -> (int, float):
    z = c
    for i in range(max_it):
        if abs(z) > 2:
            return i, abs(z)
        z = complex(abs(z.real), abs(z.imag))**power + c
    return 0,0

# Wrapper for mandebrot function which makes Julia Set
def juliaWrapper(complexParam) -> int:
    c = complexParam 

    @nb.njit([nb.types.Tuple((nb.u2, nb.f8))(nb.c16, nb.i8, nb.f8)])
    def juliaSet(com: complex, max_it: int, power: float) -> (int, float):

        z = c
        for i in range(max_it):
            if abs(z) > 1.6144:
                return i, abs(z)
            z = z**power + c
            
        return 0,0

    return juliaSet


# Finds the # of iterations for a single point 
def itFunc(arr):
    h = arr[0]
    w = arr[1]
    d = arr[2]
    zoom = pow(1.5, arr[3]) * pow(10,int(np.log10(h)))
    x_cen = arr[4]
    y_cen = arr[5]
    img = arr[6]
    fractalType = arr[7]
    mp = arr[8]
    name = arr[9]
    maxIt = arr[10]
    complexParam = arr[11]
    itArr = np.zeros((h,w))

    if fractalType == 'Mandelbrot': 
        fracFunc = mandelbrot
    if fractalType == 'Burning Ship':
        fracFunc = burningShip
    if fractalType == 'Julia Set': 
        fracFunc = juliaWrapper(complexParam)

    for i in range(w):
        if not mp:
            window['progress'].Update("{}%".format(np.round(i/w * 100, 4)))
            window.refresh()

        for j in range(h):
            it = 0
        #coordinates
            cx = i - int(w/2)
            cy = j - int(h/2)
        #scaling
            sx = (cx / (zoom)) + x_cen
            sy = (cy / (zoom)) - y_cen

            c = complex(sx,sy)
            z = complex(0,0)
            it, __ = fracFunc(c, maxIt, d) 
            itArr[j][i] = it 
    return itArr

# Find the # of iterations for a single point but also does smooth coloring 
def smoothIt(arr): 
    h = arr[0]
    w = arr[1]
    d = arr[2]
    zoom = pow(1.5, arr[3]) * pow(10,int(np.log10(h)))
    x_cen = arr[4]
    y_cen = arr[5]
    img = arr[6]
    fractalType = arr[7]
    mp = arr[8]
    name = arr[9]
    maxIt = arr[10]
    complexParam = arr[11]
    itArr = np.zeros((h,w))

    if fractalType == 'Mandelbrot': 
        fracFunc = mandelbrot
    if fractalType == 'Burning Ship':
        fracFunc = burningShip
    if fractalType == 'Julia Set': 
        fracFunc = juliaWrapper(complexParam)

    for i in range(w):
        if not mp:
            window['progress'].Update("{}%".format(np.round(i/w * 100, 4)))
            window.refresh()

        for j in range(h):
            it = 0
        #coordinates
            cx = i - int(w/2)
            cy = j - int(h/2)
        #scaling
            sx = (cx / (zoom)) + x_cen
            sy = (cy / (zoom)) - y_cen

            c = complex(sx,sy)
            
            # it = fracFunc(c,maxIt,d)
            it, z = fracFunc(c,maxIt,d)
            if it < maxIt:
                log_zn = np.log(z.real**2 + z.imag**2) / 2
                nu = np.log(log_zn/np.log(2))/np.log(2)

                it = (it - nu)

            itArr[j][i] = it

    return itArr

#naive escape time algorithm
def naive_escape(arr):
    tb = t.time()
    h = arr[0]
    w = arr[1]
    d = arr[2]
    fractalType = arr[7]
    mp = arr[8]
    name = arr[9]
    img = np.zeros((h,w,3))

    itarr = itFunc(arr)
    for i in range(w): 
        for j in range(h): 
            img[j][i] = color_dict[itarr[j][i]]
    
    cv2.imwrite(current_directory + "/{}.png".format(name), img)
    if not mp:
        window["time"].update("{} Seconds".format(np.round(t.time()-tb, 5)))    
        window["file"].update("{}.png created!".format(name))

#histogram escape time algorigthm
def histogram_escape(arr):
    tb = t.time()
    h = arr[0]
    w = arr[1]
    mp = arr[8]
    name = arr[9]
    img = arr[6]
    it_freq = [0]*(maxIt+1)
    total = 0
    it_count = itFunc(arr)

#pass 2 and 3
    for i in it_count:
        for j in i:
            it_freq[int(j)] += 1
            total += 1
#pass 4
    for i in range(w):
        if not mp:
            window['progress'].update("{}%".format(np.round(i/(2*w) * 100 + 50, 4)))
            window.refresh()

        for j in range(h):
            it = it_count[j][i]
            hue = 0
            for k in range(int(it+1)):
                hue += it_freq[int(it)]/total
            for k in range(3):
                #gotta do smth abt connecting this to the dictionary thing
                img[j][i][k] = colorsys.hls_to_rgb(0.3, 0.5,hue**0.6)[k]*255
   
    cv2.imwrite(current_directory + "/{}.png".format(name), img)
    if not mp: 
        window["time"].update("{} Seconds".format(np.round(t.time()-tb, 5)))    
        window["file"].update("{}.png created!".format(name))

# Smooth coloring algorithm
def smooth_escape(arr):
    tb = t.time()
    h = arr[0]
    w = arr[1]
    # d = arr[2]
    # zoom = pow(1.5, arr[3]) * pow(10,int(np.log10(h)))
    # x_cen = arr[4]
    # y_cen = arr[5]
    # img = arr[6]
    # fractalType = arr[7]
    mp = arr[8] 
    name = arr[9]
    # maxIt = arr[10]
    itArr = smoothIt(arr)
    img = np.zeros((h,w,3))
    for i in range(w):
        if not mp:
            window['progress'].update("{}%".format(np.round(i/w * 100, 4)))
            window.refresh()

        for j in range(h):
            it = itArr[j][i]
            pass_val= it**0.1 + 0.78
            pass_val = pass_val/2
            #0.5 0,7 0.8 v cool
            img[j][i] = np.multiply(colorsys.hls_to_rgb(pass_val, 0.5,0.85) ,255)

    cv2.imwrite(current_directory + "/{}.png".format(name), img)
    if not mp:
        window["time"].update("{} Seconds".format(np.round(t.time()-tb, 5)))    
        window["file"].update("{}.png created!".format(name))

# The function which passes all of the variables inside 
def function_of_function(height, width, zoom, d, x, y, maxIt, fractalType, parameterVary, lowerLim, upperLim, numImgs, coloringMethod, complexParam): 
    img = np.zeros((height,width,3))
    pass_arr = []

    global fileName
    for i in range(maxIt+1):
        pass_val = 1-i/25
        color_dict[i] = np.multiply(colorsys.hls_to_rgb(pass_val, 0.5,0.85) ,255)

   
    if coloringMethod == "Naive Escape":
        f = naive_escape
    if coloringMethod == "Histogram Coloring":
        f = histogram_escape
    if coloringMethod == "Smooth Escape":
        f = smooth_escape
    
    multiprocessing = True if parameterVary != "None" else False

    if multiprocessing:
        var = parameterVary 
        variedValues = np.linspace(float(lowerLim), float(upperLim), int(numImgs))

        for n in variedValues: 
            name = str(np.where(variedValues == n))
            name = name.split('[')[1].split(']')[0]
            fileName = name
            if var == 'Zoom':
                zoom = n
            if var == 'Power':
                d = n
            if var == 'X':
                x = n
            if var == 'Y':
                y = n
            if var == 'Maximum Iteration':
                maxIt = n
            
            pass_arr.append([height,width,d,zoom,x,y,img,fractalType,multiprocessing,name, maxIt, complexParam])

        t1 = t.time()
        with c.ProcessPoolExecutor() as e:
            e.map(f, pass_arr)
        window['time'].update('{} Seconds'.format(np.round(t.time()-t1, 5)))
    else:
        name = 'Fractal'
        
        if '{}.png'.format(name) in os.listdir(current_directory): 
            name = name + str(np.random.randint(1_000_000_000_000))
        fileName = name
        f([height,width,d,zoom,x,y,img,fractalType,multiprocessing,name, maxIt, complexParam])

# This is what is called 
if __name__ == '__main__':
    sg.theme("DarkTeal2")

    image_col = [[sg.Image(key ="-IMAGE-")]]

    info_col =[ [sg.Text("Pick your Parameters", justification="center", size=(32,2))], 
            [sg.Text("Height", size=(20,1)),
            	sg.InputText(default_text = '200', size=(20,1), key ='HEIGHT' )],

            [sg.Text("Width", size=(20,1)),
            	sg.InputText(default_text = '400', size=(20,1),key='WIDTH')],

            [sg.Text("Zoom", size=(20,1)),
            	sg.InputText(default_text ='2', size=(20,1),key='ZOOM')],

            [sg.Text("Power", size=(20,1)),
            	sg.InputText(default_text = '2', size=(20,1),key='POWER')],

            [sg.Text("X Coordinate", size=(20,1)),
            	sg.InputText(default_text = '-1.575', size=(20,1),key='X')],

            [sg.Text("Y Coordinate", size=(20,1)),
            	sg.InputText(default_text = '0.019', size=(20,1),key='Y')],

            [sg.Text("Maximum Iterations", size=(20,1)),
            	sg.InputText(default_text = '200', size=(20,1), key='maxIt')], 

            [sg.Text("Fractal Type", size=(20,1)),
            	sg.InputCombo(("Mandelbrot", "Burning Ship", "Julia Set"),
            	    size=(20,1), default_value= "Mandelbrot", key='fractalType', enable_events = True)],
            [sg.Text("Complex Parameter", size=(20,1)), 
                sg.InputText(default_text = "1+5j", size=(20,1), key = 'complexParam', disabled=True)], 
            [sg.Text("Parameter to vary", size=(20,1)),
            	sg.InputCombo(('Zoom', 'Power', 'X', 'Y', 'Maximum Iteration','None'),
                    size=(20, 1), default_value = "None", key='parameterVary', enable_events = True)],

            [sg.Text("Lower Limit", size=(20,1)), 
                sg.InputText(tooltip="Lower Limit for computation", key = 'lowerLim', size=(20,1), disabled=True)],

            [sg.Text("Upper Limit", size=(20,1)),
                sg.InputText(tooltip="Upper Limit for Computation", key='upperLim', size=(20,1), disabled=True)], 

            [sg.Text("# of Images", size=(20,1)), 
            	sg.InputText(tooltip= "How many images?", key='increment', size=(20,1), disabled=True)],

            [sg.Text("Coloring Method", size=(20,1)),
            	sg.InputCombo(("Naive Escape", "Histogram Coloring", "Smooth Escape"),
            	    size=(20,1), default_value= "Naive Escape", key='coloringMethod')],

            [sg.Text("Progress:", size=(20,1)), sg.Text("", key="progress", size=(20,1) )],
               
            [sg.Text("Time Taken:", size=(20,1)), sg.Text("", key="time", size=(20,1))],

            [sg.Text("", key='file', size=(32,1))],

            [sg.Button("Compute", key='compute', size=(20,1)), sg.Button("Show Image!", key='showimg', disabled=True, size=(20,1))] ]
    
    # Event Loop to process "events" and get the "values" of the inputs
    window = sg.Window('Fractal Visualizer',[[sg.Column(image_col) ,sg.Column(info_col)]], font="Iosevka")
    while True:
        event, values = window.read()

        # Dims the complex parameter field when th julia set is not selected
        if event == "fractalType":
            if values['fractalType'] == 'Julia Set':
                window['complexParam'].update(disabled=False)
            else: 
                window['complexParam'].update(disabled=True)

        # Dims the correct parameter field when a certain varying parameter is picked 
        if event == "parameterVary":
            if values['parameterVary'] == 'Zoom': 
                window['ZOOM'].update(disabled=True)
                window['maxIt'].update(disabled=False)
                window['POWER'].update(disabled=False)
                window['X'].update(disabled=False)
                window['Y'].update(disabled=False)
                window['lowerLim'].update(disabled=False)
                window['upperLim'].update(disabled=False)
                window['increment'].update(disabled=False)

            elif values['parameterVary'] == 'Power': 
                window['POWER'].update(disabled=True)
                window['ZOOM'].update(disabled=False)
                window['maxIt'].update(disabled=False)
                window['X'].update(disabled=False)
                window['Y'].update(disabled=False)
                window['lowerLim'].update(disabled=False)
                window['upperLim'].update(disabled=False)
                window['increment'].update(disabled=False)

            elif values['parameterVary'] == 'X':
                window['X'].update(disabled=True)
                window['POWER'].update(disabled=False)
                window['maxIt'].update(disabled=False)
                window['ZOOM'].update(disabled=False)
                window['Y'].update(disabled=False)
                window['lowerLim'].update(disabled=False)
                window['upperLim'].update(disabled=False)
                window['increment'].update(disabled=False)

            elif values['parameterVary'] == 'Y':
                window['Y'].update(disabled=True)
                window['maxIt'].update(disabled=False)
                window['X'].update(disabled=False)
                window['POWER'].update(disabled=False)
                window['ZOOM'].update(disabled=False)
                window['lowerLim'].update(disabled=False)
                window['upperLim'].update(disabled=False)
                window['increment'].update(disabled=False)

            elif values['parameterVary'] == 'Maximum Iteration':
                window['maxIt'].update(disabled=True)
                window['Y'].update(disabled=False)
                window['X'].update(disabled=False)
                window['POWER'].update(disabled=False)
                window['ZOOM'].update(disabled=False)
                window['lowerLim'].update(disabled=False)
                window['upperLim'].update(disabled=False)
                window['increment'].update(disabled=False)

            elif values['parameterVary'] == 'None': 
                window['maxIt'].update(disabled=False)
                window['Y'].update(disabled=False)
                window['X'].update(disabled=False)
                window['POWER'].update(disabled=False)
                window['ZOOM'].update(disabled=False)
                window['lowerLim'].update(disabled=True)
                window['upperLim'].update(disabled=True)
                window['increment'].update(disabled=True)

        # Closes the window when the X is clicked
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            break
       
        # Runs the process to carry out the computation of the image, using all the variables obtained from the gui 
        if event == "compute":
            try: 
                height = abs(int(values['HEIGHT']))
                width = abs(int(values['WIDTH']))
                zoom = float(values['ZOOM'])
                d = abs(float(values['POWER']))
                x = float(values['X'])
                y = float(values['Y'])
                maxIt = abs(int(values['maxIt']))
                fractalType = values['fractalType'] 
                parameterVary = values['parameterVary'] 
                if parameterVary != 'None':
                    lowerLim = float(values['lowerLim'])
                    upperLim = float(values['upperLim'])
                    noImgs = int(values['increment'])
                else: 
                    lowerLim,upperLim, noImgs = 0,0,0
                coloringMethod = values['coloringMethod']
                complexParam = complex(''.join(values['complexParam'].split(" ")))
            except Exception as e: 
                sg.PopupOK('Check Data and try again! \n Error:{}'.format(e), keep_on_top = True, no_titlebar = True)                
            finally: 
                function_of_function(height, width, zoom, d, x, y, maxIt, fractalType, parameterVary, lowerLim, upperLim, noImgs, coloringMethod,complexParam)    
                window['showimg'].update(disabled=False)

        # Opens the folder or shows the image when a button is clicked
        if event == 'showimg':
            window["compute"].update(disabled=True)
            filePath = "{}/{}.png".format(current_directory, fileName)
            image = Image.open(filePath)
            image.thumbnail((800,800))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window["-IMAGE-"].update(data=bio.getvalue())
            window["compute"].update(disabled=False)

