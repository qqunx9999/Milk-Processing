import blynklib
import time
import random
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
BLYNK_AUTH = 'UwYV8t66fXm1sIBrAOtb7VOY4c5704q0'
blynk = blynklib.Blynk(BLYNK_AUTH)

'''
initial assigned :
V0 for Liter slider
V1 for Boxes/Bottle unit selected
V2 for Selected size 
'''

# register handler for virtual pin (INPUT things from mobile)
@blynk.handle_event('write V0') #Get Milk_liter
def write_virtual_pin_handler(pin, value):
    global milk_liter
    milk_liter = float(value[0])
    print(f"{milk_liter} Liters selected")
    blynk.set_property(pin, 'color', '#32CD32')
    
@blynk.handle_event('write V1') #Unit Selector
def write_virtual_pin_handler(pin, value):
    '''
    0 for UHT
    1 for Pasterized
    '''
    global unit_selected,IsSelect,Unit
    unit_selected = int(value[0])
    unit_selected-=1
    IsSelect = 1
    SetSize()
    Unit = "Bottle" if(unit_selected==1) else "Box"
    MilkType = "UHT" if(unit_selected==0) else "Pasterized"
    print(f"{MilkType} selected in {Unit} unit")
    Unit = "Bottles" if(unit_selected=="Bottle") else "Boxes"
    blynk.set_property(pin, 'color', '#32CD32')




@blynk.handle_event('write V2') #Size selected
def write_virtual_pin_handler(pin, value):
    global size_selected,div,size
    size_selected = int(value[0])
    size_selected-=1 #0,1,2
    if(not unit_selected): 
        if(size_selected == 0): # 125 mL
            size = 125
        elif(size_selected == 1): # 180 mL
            size = 180
        else: # 225 mL
            size = 225
    else:
        if(size_selected == 0): # 200 mL
            size = 200
        elif(size_selected == 1): # 830 mL
            size = 830
        else: # 2000 mL
            size = 2000
    div = size/1000 #Unit Conversion
    print(f"{size} mL Selected")
    blynk.set_property(pin, 'color', '#32CD32')

@blynk.handle_event('write V3') #Unit Selector
def write_virtual_pin_handler(pin, value):
    initialize()

@blynk.handle_event('write V5') #Calculate Button 
def write_virtual_pin_handler(pin, value):
    global IsCalculate,milk_liter,colour
    if(IsReady()):
        IsCalculate = 1
        colour = count%(len(colours))
        blynk.set_property(5, 'onLabel', 'Ready')
        blynk.set_property(5, 'onColor', colours[colour])
        blynk.set_property(5, 'offLabel', 'Ready')
        blynk.set_property(5, 'offColor', colours[colour])
    else:
        blynk.set_property(5, 'offLabel', 'Not Ready')
        blynk.set_property(5, 'offColor', '#000000')
        blynk.set_property(5, 'onLabel', 'Not Ready')
        blynk.set_property(5, 'onColor', '#000000')

def ready():
    text = ""
    for i in range(len(R)):
        text = text+R[i]
        blynk.set_property(5,"offLabel", text)
        blynk.set_property(5, 'offColor', '#FFFFFF')
##        blynk.set_property(5,"onLabel", text)
##        blynk.set_property(5, 'onColor', '#FFFFFF')
        sleep((Golden)/10) if(i!=(len(L)-1)) else sleep(1.8)
        

        
def IsReady(a="Do nothing"):
    IsWork = False
    if(div != 1 and unit_selected !=-1 and milk_liter >4):
        if(a.lower() == "set"):
            try:
                t.start()
            except (RuntimeError):
                pass
##            blynk.set_property(5, 'offLabel', 'Ready')
##            blynk.set_property(5, 'offColor', '#FFFFFF')
        IsWork = True
    return IsWork

def SetSize():
    '''
    Use for Set V2 -> Correct size of UHT,Pasterized
    '''
    if(not unit_selected): #Are there UHT ?
        blynk.set_property(2, 'labels', '125 mL', '180 mL', '225 mL')
    else: #Are there Pasterized
        blynk.set_property(2, 'labels', '200 mL', '830 mL', '2000 mL')
        
def Milk_Processing():
    global MilkError,ErrorVariable,IsCalculate,nmilk,milk_liter,div,Pass,Fail
    err_each = []
    err_var = []
    global nmilk
    nmilk = int(milk_liter/div)
    print(f"Total milk about : {nmilk}")
    for i in range(nmilk):
        err_each = [uniform(0,100),uniform(0,100),uniform(0,100)] #BoxDefect as err_each[0],WorkerDefect as err_each[1],MachineDefect as err_each[2] Respectively
        err_each[0] = 0 if(err_each[0] >0.1) else err_each[0]
        err_each[1] = 0 if(err_each[1] >0.2) else err_each[1]
        err_each[2] = 0 if(err_each[2] >0.3) else err_each[2]
        err_var = [type(x) is float for x in err_each] #if each error is pass will kepp value 1,fail to 0
        #We not set too 0 at first,cuz it possible that can be 
        status = "P" if(type(sum(err_each)) is int) else "F" #If there pass for all,will be 0 (int 0) but if there still have any random the type will be float.
        err_each.append(status)
        MilkError.append(err_each)
        ErrorVariable.append(err_var)
    for x in MilkError:
        val = 1 if(x[3]=="P") else 0
        Pass.append(val)
    Fail = [not(x) for x in Pass]
    JustASec()
    Presentation()
    
def JustASec():
    mode = ["onLabel","offLabel"]
    text = ""
    sleep(Golden/9)
    for i in range(len(L)):
        text = text+L[i]
        for x in mode:
            blynk.set_property(5,x, text)
            blynk.set_property(5, 'onColor', '#000080')
            blynk.set_property(5, 'offColor', '#000080')
        sleep((Golden/10)) if(i!=(len(L)-1)) else sleep(1.8)
    for x in mode:
        blynk.set_property(5,x, "Success")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden/10)
    for x in mode:
        blynk.set_property(5,x, "Success!")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden/10)
    for x in mode:
        blynk.set_property(5,x, "Success!!")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden/10)
    for x in mode:
        blynk.set_property(5,x, "Success!!!")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden/2)
    for x in mode:
        blynk.set_property(5,x, "CLOSE THE")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden)
    for x in mode:
        blynk.set_property(5,x, "GRAPH TO")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden)
    for x in mode:
        blynk.set_property(5,x, "CONTINUE")
        blynk.set_property(5, 'onColor', '#000080')
        blynk.set_property(5, 'offColor', '#000080')
    sleep(Golden/2)

def Presentation():
    global MilkError,ErrorVariable,IsCalculate,nmilk,milk_liter,div,Pass,Fail,count,colour,size,MilkFail,MilkPass,TimeEx
    MilkPass = sum(Pass)
    MilkFail = nmilk - MilkPass
    TimeEx = milk_liter*(3600/2000) #Estimated time
    time_unit = [" hour"," minute"," second"]
    if(TimeEx >=3600):
        hr = int(TimeEx//3600)
        minute = int((TimeEx-hr*3600)//60)
        sec = int(TimeEx%60)
        if(hr >=2):
            time_unit[0] = time_unit[0]+"s"
        if(minute>=2):
            time_unit[1] = time_unit[1]+"s"
        if(sec>=2):
            time_unit[2] = time_unit[2]+"s"
        TimeEx = str(hr) + time_unit[0]+" "+str(minute)+" "+ time_unit[1] +" "+ str(sec)+time_unit[2]
    elif TimeEx >= 60:
        minute = int((TimeEx)//60)
        sec = int(TimeEx%60)
        if(minute>=2):
            time_unit[1] = time_unit[1]+"s"
        if(sec>=2):
            time_unit[2] = time_unit[2]+"s"
        TimeEx = str(minute)+ time_unit[1] +" "+ str(sec)+time_unit[2]
    else:
        TimeEx = str(TimeEx)+time_unit[2]
    box,work,mac = sum([x[0] for x in ErrorVariable]),sum([x[1] for x in ErrorVariable]),sum([x[2] for x in ErrorVariable])
    print(f"Milk passed about {MilkPass}")
    print(f"Milk failed about {MilkFail}")
    print(f"Failed Percent is {MilkFail/MilkPass*100:.2f} %")
    print(f"BoxEff = {box/nmilk*100:.2f} %,WorkDef = {work/nmilk*100:.2f} %,MachEff = {mac/nmilk*100:.2f} %")
    print(f"Estimated Time about {TimeEx}")
    cumulative_error_plot()
    print(45*"-")
    print()
    blynk.set_property(5, 'onColor', colours[colour])
    blynk.set_property(5, 'onLabel', 'Ready')
    blynk.set_property(5, 'offColor', colours[colour])
    blynk.set_property(5, 'offLabel', 'Ready')
    IsCalculate = 0
    count +=1
    MilkError,ErrorVariable,Pass,Fail,ErrorCum = [],[],[],[],[]

def cumulative_error_plot():
    global MilkError,ErrorVariable,IsCalculate,nmilk,milk_liter,div,Pass,Fail,count,colour,ErrorCum,Unit,MilkFail,MilkPass,TimeEx
    
##    for i in range(nmilk):
##        err = Fail[i]/(i+1)
##        ErrorCum.append(err)
    ErrorCum = np.cumsum(Fail)
    y=[]
    ExampleNo = int(nmilk/400) #if nmilk <= 500 -> ExampleNo = 1 ;Run on every example
    x = np.linspace(1,nmilk,ExampleNo) if(nmilk>=ExampleNo) else np.linspace(1,nmilk,1)
    x = list(map(int,x))
    for n in x:
        y.append(ErrorCum[n-1])
    y = np.array(y)
    plt.plot(x,y,label="Cumulative of error")
    plt.grid(True);plt.xlabel(f"Number of example ({Unit})")
    plt.ylabel("Number of failure (Time)")
    blynk.virtual_write(6, (f"{nmilk} -> {MilkPass}/{MilkFail} {Unit} , {(MilkFail/nmilk):.6f} %"))
    blynk.virtual_write(7, (f"{TimeEx}"))
    plt.show()

def initialize():
    global IsSelect,IsCalculate,unit_selected,ErrorVariable,Pass,Fail,ErrorCum,Unit,stop_thread
    global MilkError,div,milk_liter,nmilk,count,colours,colour,MilkType,R,L,t,Golden,TimeEx
    Golden = (1 + 5 ** 0.5) / 2
    R = "Ready"
    L = "Loading..."
    ErrorCum = []
    IsSelect = 0
    colours = ["#FFFFFF"]
    stop_thread = 1
    IsCalculate = 0
    unit_selected = -1
    div = 1
    milk_liter = 0
    nmilk = 0
    count = 0
    t = Thread(target=ready)
    MilkError,ErrorVariable,Pass,Fail,ErrorCum = [],[],[],[],[]

    AllPin = [0,1,2,5]
    blynk.run()
    for i in AllPin:
        blynk.virtual_write(i, 0)
    blynk.set_property(0, 'color', '#FF0000')
    blynk.set_property(1, 'color', '#FF0000')
    blynk.set_property(2, 'color', '#FF0000')
    blynk.set_property(5, 'offLabel', 'Not Ready')
    blynk.set_property(5, 'offColor', '#FF0000')
    blynk.set_property(5, 'onLabel', 'Ready')
    blynk.set_property(5, 'onColor', '#FFFFFF')
    blynk.virtual_write(6, (" "))
    blynk.virtual_write(7, (" "))

    

from random import uniform
# Main Program
initialize()
while True:
    blynk.run()
    IsReady("SET")
    if(IsCalculate):
        Milk_Processing()
    #blynk.virtual_write(1, str(t))
