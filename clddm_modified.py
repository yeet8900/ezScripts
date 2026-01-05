from datetime import datetime
import math
logfile = "log.txt"

class Transmitter:
    def __init__(self, clddm, psb, category,reqCourseWidth,clearance_90,clearance_150):
        self.current_DDM = clddm
        self.current_Psb = psb
        self.required_course_width = reqCourseWidth
        self.width_narrow = 51.48
        self.width_wide = 36.52
        self.clearance_90 = clearance_90
        self.clearance_150 = clearance_150
        self.category = category
        match category:
            case 1:
                self.clddm_90 = 15.33
                self.clddm_150= -15.33
            case 2:
                self.clddm_90 = 11.07
                self.clddm_150= -11.07
            case _:
                self.clddm_90 = 8.94
                self.clddm_150= -8.94

        
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
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_90 is {transmitter.clddm_90} microAmps, new CL_DDM_90 is {transmitter.current_DDM} microAmps \n")
        transmitter.clddm_90= round(new_clddm_90,3)
        print(f"NEW CL_DDM_90 IS  ******* {transmitter.clddm_90}μA ({round(transmitter.current_DDM * 0.1033,3)} %) ******, type \"exit\" to exit ",)

def modifyClddm150(transmitter:Transmitter):
    while True:
        printTable(transmitter)
        user_input = input('Enter new value of clddm 150, type \"exit\" to exit  \n')
        if user_input.lower() == "exit":
            break
        try:
            new_clddm_90 = round(float(user_input),3)
        except ValueError:
            print("Delta should be numeric")
            continue
        with(open(logfile,"a") as f):
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_150 is {transmitter.clddm_90} microAmps, new CL_DDM_90 is {transmitter.current_DDM} microAmps \n")
        transmitter.clddm_90= round(new_clddm_90,3)
        print(f"NEW CL_DDM_150 IS  ******* {transmitter.clddm_90}μA ({round(transmitter.current_DDM * 0.1033,3)} %) ******",)


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
        print(f"NEW PSB IS  ******* {transmitter.current_Psb} ******, type \"exit\" to exit ",)
transmitters = {}  
print("enter category (1 or 2 or 3, 3 is default)")
category = int(input())
print("enter required course width")
reqCourseWidth = round(float(input()),3)
for a in range(1,3):
    print(f"enter the parameters for transmitter {a} (comma separated) \nexample: initial cl_ddm,initial_psb,clearance_90,clearance_150\n")
    x = input()
    listOfParameters = x.split(",")
    listOfParameters = [round(float(a),3) for a in listOfParameters]
    clddm,psb,clearance_90,clearance_150 = listOfParameters
    transmitters[f"transmitter{a}"]= Transmitter(clddm,psb,category,reqCourseWidth,clearance_90,clearance_150)
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

while(True):
    print(
    "What do you want to change? Select a number from this menu:\n"
    "1.Tx1 clddm \n"
    "2.Tx1 psb \n"
    "3.Tx1 clddm_90 \n"
    "4.Tx1 clddm_150\n"
    "5.Tx1 width_narrow\n"
    "6.Tx1 width_wide\n"
    "7. Tx2 clddm\n"
    "8. Tx2 psb\n"
    "9. Tx2 clddm_90\n"
    "10. Tx2 clddm_150\n"
    "11. Tx2 width_narrow\n"
    "12. Tx2 width_wide\n"
    )
    choice = int(input())
    match choice:
        case -1:
            print("current states transmitters are:")
        # Tx1
        case 1:
            print(f"modifying clddm transmitter1, current value is {transmitters["transmitter1"].current_DDM} ")
            modifyClddm(transmitters["transmitter1"])
        case 2:
            print(f"modifying psb transmitter1, current value is {transmitters["transmitter1"].current_Psb} ")
            modifyPsb(transmitters["transmitter1"])
        case 3:
            print(f"modifying clddm_90 transmitter1 current value is {transmitters["transmitter1"].clddm_90}")
            modifyClddm90(transmitters["transmitter1"])
        case 4:
            print("You selected t4 Tx1")
        case 5:
            print("You selected t5 Tx1")
        case 6:
            print("You selected t6 Tx1")

        # Tx2
        case 7:
            print(f"modifying clddm transmitter2, current value is {transmitters["transmitter2"].current_DDM} ")
            modifyClddm(transmitters["transmitter2"])
        case 8:
            print(f"modifying psb transmitter2, current value is {transmitters["transmitter2"].current_Psb} ")
            modifyPsb(transmitters["transmitter2"])
        case 9:
            print(f"modifying clddm_90 transmitter2 current value is {transmitters["transmitter2"].clddm_90}")
            modifyClddm90(transmitters["transmitter2"])
        case 10:
            print("You selected t4 Tx2")
        case 11:
            print("You selected t5 Tx2")
        case 12:
            print("You selected t6 Tx2")

        case _:
            print("Invalid choice")





