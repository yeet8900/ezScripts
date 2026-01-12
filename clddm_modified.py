from datetime import datetime
import math
logfile = "log.txt"
datafile = "state.txt"
print("do you want to restore to previous state? (y/n)")
restore = input().lower()
if restore == 'y':
    print("restoring previous state is not yet implemented")
    with open(datafile, "r") as f:
        lines = f.readlines()
        # instantiate python objects from text file dbs here.



class Transmitter:
    def __init__(self, clddm, psb, category,reqCourseWidth,clearance_90,clearance_150):
        self.current_DDM = clddm
        self.current_Psb = psb
        self.required_course_width = reqCourseWidth
        self.width_narrow = self.current_Psb + 20 * math.log10(1.18)
        self.width_wide = self.current_Psb - 20 * math.log10(1.18)
        self.clearance_90 = clearance_90
        self.clearance_150 = clearance_150
        self.category = category
        match category:
            case 1:
                self.clddm_90 = 15.33
                self.clddm_150= -15.33
                self.constraints = [12,20]
            case 2:
                self.clddm_90 = 11.07
                self.clddm_150= -11.07
                self.constraints = [10,15]
            case _:
                self.clddm_90 = 8.94
                self.clddm_150= -8.94
                self.constraints = [5,12]
        
dataClddmCat1 = [(31, 13.20),
(32, 13.63),
(33, 14.05),
(34, 14.48),
(35, 14.90),
(36, 15.33),
(37, 15.75),
(38, 16.18),
(39, 16.61),
(40, 17.03),
]
dataClddmCat2 = [
                (24, 10.22),
                (25, 10.64),
                (26, 11.07),
                (27, 11.50),
                (28, 11.92),
                (29, 12.35),
                (30, 12.77),
            ]
dataClddmCat3 = [
    (15, 6.39),
    (16, 6.81),
    (17, 7.24),
    (18, 7.66),
    (19, 8.09),
    (20, 8.52),
    (21, 8.94),
    (22, 9.37),
    (23, 9.79),
    (24, 10.22),
    (25, 10.64),
]


def logState():
    with open(logfile, "a") as f:
        f.write(f"\n--- Initial values for transmitter{a} ---\n")
        f.write(f"Current DDM: {transmitters[f'transmitter{a}'].current_DDM}\n")
        f.write(f"Current PSB: {transmitters[f'transmitter{a}'].current_Psb}\n")
        f.write(f"Required course width: {transmitters[f'transmitter{a}'].required_course_width}\n")
        f.write(f"Width narrow: {transmitters[f'transmitter{a}'].width_narrow}\n")
        f.write(f"Width wide: {transmitters[f'transmitter{a}'].width_wide}\n")
        f.write(f"Clearance 90: {transmitters[f'transmitter{a}'].clearance_90}\n")
        f.write(f"Clearance 150: {transmitters[f'transmitter{a}'].clearance_150}\n")
        f.write(f"CLDDM 90: {transmitters[f'transmitter{a}'].clddm_90}\n")
        f.write(f"CLDDM 150: {transmitters[f'transmitter{a}'].clddm_150}\n")
        f.write("-------------------------------\n")

def changeCourseWidth(transmitter:Transmitter, negative: bool):
    print(f"Specification value @ 18% is {transmitter.width_narrow}  dbm \n")
    while True:
        user_input = input('Enter any value (percentage) between 5 to 20, "exit" to exit\n')
        if user_input.lower() == "exit":
            break
        try:
            percentValue = round(float(user_input)/100,3)
            math.log10(percentValue)
        except ValueError:
            print("Value should be non-negative")
            continue
        increaseValue = 1 + percentValue
        with(open(logfile,"a") as f):
            if (negative):
                f.write(f"{datetime.now().time().replace(microsecond=0)} Course width wide PSB is {transmitter.width_narrow}, change is {user_input}%, new PSB is {transmitter.current_Psb - 20 * math.log10(increaseValue)} \n")
            else:
                f.write(f"{datetime.now().time().replace(microsecond=0)} Course width narrow PSB is {transmitter.width_narrow}, change is {user_input}%, new PSB is {transmitter.current_Psb + 20 * math.log10(increaseValue)} \n")
        
        if(negative):
            transmitter.width_wide = transmitter.current_Psb - 20 * math.log10(increaseValue) 
        else:
            transmitter.width_narrow = transmitter.current_Psb + 20 * math.log10(increaseValue)
        transmitter.width_narrow = round(transmitter.width_narrow,3)
        transmitter.width_wide = round(transmitter.width_wide,3)
        if(negative):
            print(f"NEW COURSE WIDTH WIDE PSB IS  ******* {transmitter.width_wide} ******, type \"exit\" to exit \n",)
        else:
            print(f"NEW COURSE WIDTH NARROW PSB IS  ******* {transmitter.width_narrow} ******, type \"exit\" to exit \n",)

def printTable(transmitter:Transmitter):
    print("The list of values are:")
    print(f"{'Feet':<6} {'Microamps':>10}")
    if(transmitter.category == 1):
        for feet, microamps in dataClddmCat1:
            print(f"{feet:<6}\' {microamps:>10.2f}")
    elif (transmitter.category == 2):
        for feet, microamps in dataClddmCat2:
            print(f"{feet:<6} {microamps:>10.2f}")
    else:
        for feet, microamps in dataClddmCat3:
            print(f"{feet:<6}\' {microamps:>10.2f}")
        
def modifyClddm90(transmitter:Transmitter):
    while True:
        printTable(transmitter)
        user_input = input('Enter new value of clddm 90, type \"exit\" to exit\n')
        if user_input.lower() == "exit":
            break
        try:
            new_clddm_90 = round(float(user_input),3)
        except ValueError:
            print("Delta should be numeric")
            continue
        with(open(logfile,"a") as f):
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_90 is {transmitter.clddm_90} microAmps, new CL_DDM_90 is {transmitter.clddm_90} microAmps \n")
        transmitter.clddm_90= round(new_clddm_90,3)
        print(f"NEW CL_DDM_90 IS  ******* {transmitter.clddm_90}μA ({round(transmitter.current_DDM * 0.1033,3)} %) ******, type \"exit\" to exit ",)

def modifyClddm150(transmitter:Transmitter):
    while True:
        printTable(transmitter)
        user_input = input('Enter new value of clddm 150, type \"exit\" to exit  \n')
        if user_input.lower() == "exit":
            break
        try:
            new_clddm_150 = round(float(user_input),3)
        except ValueError:
            print("Delta should be numeric")
            continue
        with(open(logfile,"a") as f):
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_150 is {transmitter.clddm_150} microAmps, new CL_DDM_90 is {transmitter.clddm_150} microAmps \n")
        transmitter.clddm_150= round(new_clddm_150,3)
        print(f"NEW CL_DDM_150 IS  ******* {transmitter.clddm_150}μA ({round(transmitter.clddm_150 * 0.1033,3)} %) ******",)

def modifyClddm(transmitter:Transmitter):
    while True:
        user_input = input('enter Delta value (μA) (FIU): ')
        if user_input.lower() == "exit":
            break
        try:
            delta = round(float(user_input),3)
        except ValueError:
            print("Delta should be numeric")
            continue
        with(open(logfile,"a") as f):
            f.write(f"{datetime.now().time().replace(microsecond=0)} currentDDM is {transmitter.current_DDM} microAmps, delta is {delta} microAmps, new DDM is {delta + transmitter.current_DDM} microAmps \n")
        transmitter.current_DDM = delta + transmitter.current_DDM
        transmitter.current_DDM = round(transmitter.current_DDM,3)
        print(f"NEW DDM IS  ******* {transmitter.current_DDM}μA ({round(transmitter.current_DDM * 0.1033,3)} %) ******, type \"exit\" to exit ",)

def modifyPsb(transmitter:Transmitter):
    while True:
        user_input = input('Enter course width value (in degrees) (FIU): ')
        if user_input.lower() == "exit":
            break
        try:
            course_width_FIU = round(float(user_input),3)
            math.log10(course_width_FIU)
        except ValueError:
            print("Course width should be numeric and non-negative")
            continue
        with(open(logfile,"a") as f):
            f.write(f"{datetime.now().time().replace(microsecond=0)} CurrentPSB is {transmitter.current_Psb}, delta is {course_width_FIU}, new PSB is {transmitter.current_Psb + 20 * math.log10(course_width_FIU/transmitter.required_course_width)} \n")
        transmitter.current_Psb = transmitter.current_Psb + 20 * math.log10(course_width_FIU/transmitter.required_course_width) 
        transmitter.current_Psb = round(transmitter.current_Psb,3)
        print(f"NEW PSB IS  ******* {transmitter.current_Psb} ******, type \"exit\" to exit \n",)

transmitters = {}  
tx1 = transmitters["transmitter1"]
tx2 = transmitters["transmitter2"]


if( restore == 'n'):
    print("enter category (1 or 2 or 3, 3 is default)")
    while(True):
        try:
            category = (input())
            category = int(category)
            break
        except ValueError:
            print("Category must be between 1 to 3")

    print("enter required course width")

    while(True):
        try:
            reqCourseWidth = input()
            reqCourseWidth = round(float(reqCourseWidth),3)
            break
        except ValueError:
            print("Category must be between 1 to 3")

    for a in range(1,3):
        print(f"enter the parameters for transmitter {a} (comma separated) \nexample: initial cl_ddm,initial_psb,clearance_90,clearance_150\n")
        x = input()
        listOfParameters = x.split(",")
        listOfParameters = [round(float(a),3) for a in listOfParameters]
        clddm,psb,clearance_90,clearance_150 = listOfParameters
        transmitters[f"transmitter{a}"]= Transmitter(clddm,psb,category,reqCourseWidth,clearance_90,clearance_150)
        logState()



while(True):
    print(
    f"What do you want to change? Select a number from this menu:\n"
    f"1.  Tx1 clddm         {tx1.current_DDM} μA\n"
    f"2.  Tx1 psb           {tx1.current_Psb} dBm\n"
    f"3.  Tx1 clddm_90      {tx1.clddm_90} μA\n"
    f"4.  Tx1 clddm_150     {tx1.clddm_150} μA\n"
    f"5.  Tx1 width_narrow  {tx1.width_narrow:.2f} dBm\n"
    f"6.  Tx1 width_wide    {tx1.width_wide:.2f} dBm\n"
    f"7.  Tx2 clddm         {tx2.current_DDM} μA\n"
    f"8.  Tx2 psb           {tx2.current_Psb} dBm\n"
    f"9.  Tx2 clddm_90      {tx2.clddm_90} μA\n"
    f"10. Tx2 clddm_150     {tx2.clddm_150} μA\n"
    f"11. Tx2 width_narrow  {tx2.width_narrow:.2f} dBm\n"
    f"12. Tx2 width_wide    {tx2.width_wide:.2f} dBm\n"
    )
    
    while(True):
        try:
            choice = input()
            choice = int(choice)
            break
        except ValueError:
            print("choice must be a number between 1-12")

    match choice:
        case -1:
            print("current states transmitters are:")
        # Tx1
        case 1:
            print(f"modifying clddm transmitter1, current value is {tx1.current_DDM} ")
            modifyClddm(tx1)
        case 2:
            print(f"modifying psb transmitter1, current value is {tx1.current_Psb} ")
            modifyPsb(tx1)
        case 3:
            print(f"modifying clddm_90 transmitter1 current value is {tx1.clddm_90}")
            modifyClddm90(tx1)
        case 4:
            print(f"modifying clddm_150 transmitter1 current value is {tx1.clddm_150}")
            modifyClddm150(tx1)
        case 5:
            changeCourseWidth(tx1,False)
        case 6:
            changeCourseWidth(tx1,True)

        # Tx2
        case 7:
            print(f"modifying clddm transmitter2, current value is {tx2.current_DDM} ")
            modifyClddm(tx2)
        case 8:
            print(f"modifying psb transmitter2, current value is {tx2.current_Psb} ")
            modifyPsb(tx2)
        case 9:
            print(f"modifying clddm_90 transmitter2 current value is {tx2.clddm_90}")
            modifyClddm90(tx2)
        case 10:
            print(f"modifying clddm_150 transmitter2 current value is {tx2.clddm_150}")
            modifyClddm150(tx2)
        case 11:
            changeCourseWidth(tx2,False)
        case 12:
            changeCourseWidth(tx2,True)

        case _:
            print("Invalid choice")




#todo :
#change clddm90 output format, mention units, constrain values, shift current val display further down
# print vals for each parameter in transmitter in the menu
# change formatting, optimize code