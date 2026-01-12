from datetime import datetime
import math

logfile = "log.txt"
datafile = "data"

class Transmitter:
    def __init__(self, clddm, psb, category, reqCourseWidth, clearance_90, clearance_150):
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
                self.clddm_150 = -15.33
                self.constraints = [12, 20]
            case 2:
                self.clddm_90 = 11.07
                self.clddm_150 = -11.07
                self.constraints = [10, 15]
            case _:
                self.clddm_90 = 8.94
                self.clddm_150 = -8.94
                self.constraints = [5, 12]

dataClddmCat1 = [(31, 13.20), (32, 13.63), (33, 14.05), (34, 14.48), (35, 14.90),
                 (36, 15.33), (37, 15.75), (38, 16.18), (39, 16.61), (40, 17.03)]

dataClddmCat2 = [(24, 10.22), (25, 10.64), (26, 11.07), (27, 11.50), (28, 11.92),
                 (29, 12.35), (30, 12.77)]

dataClddmCat3 = [(15, 6.39), (16, 6.81), (17, 7.24), (18, 7.66), (19, 8.09),
                 (20, 8.52), (21, 8.94), (22, 9.37), (23, 9.79), (24, 10.22), (25, 10.64)]

def saveStateToFile(transmitters):
    """Save all transmitter states to the datafile"""
    with open(datafile, "w") as f:
        for tx_name in ["transmitter1", "transmitter2"]:
            if tx_name in transmitters:
                tx = transmitters[tx_name]
                f.write(f"{tx_name}\n")
                f.write(f"CLDDM: {tx.current_DDM}\n")
                f.write(f"current_Psb: {tx.current_Psb}\n")
                f.write(f"required_course_width: {tx.required_course_width}\n")
                f.write(f"clearance_90: {tx.clearance_90}\n")
                f.write(f"clearance_150: {tx.clearance_150}\n")
                f.write(f"category: {tx.category}\n")
                f.write(f"clddm_90: {tx.clddm_90}\n")
                f.write(f"clddm_150: {tx.clddm_150}\n")
                f.write(f"width_narrow: {tx.width_narrow}\n")
                f.write(f"width_wide: {tx.width_wide}\n")
                f.write("\n")

def loadStateFromFile():
    """Load transmitter states from the datafile"""
    transmitters = {}
    try:
        with open(datafile, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        
        current_tx = None
        tx_data = {}
        
        for line in lines:
            if line.startswith("transmitter"):
                if current_tx and tx_data:
                    transmitters[current_tx] = Transmitter(
                        tx_data['CLDDM'],
                        tx_data['current_Psb'],
                        tx_data['category'],
                        tx_data['required_course_width'],
                        tx_data['clearance_90'],
                        tx_data['clearance_150']
                    )
                    transmitters[current_tx].clddm_90 = tx_data['clddm_90']
                    transmitters[current_tx].clddm_150 = tx_data['clddm_150']
                    transmitters[current_tx].width_narrow = tx_data['width_narrow']
                    transmitters[current_tx].width_wide = tx_data['width_wide']
                
                current_tx = line
                tx_data = {}
            elif line and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key == 'category':
                    tx_data[key] = int(value)
                else:
                    tx_data[key] = float(value)
        
        if current_tx and tx_data:
            transmitters[current_tx] = Transmitter(
                tx_data['CLDDM'],
                tx_data['current_Psb'],
                tx_data['category'],
                tx_data['required_course_width'],
                tx_data['clearance_90'],
                tx_data['clearance_150']
            )
            transmitters[current_tx].clddm_90 = tx_data['clddm_90']
            transmitters[current_tx].clddm_150 = tx_data['clddm_150']
            transmitters[current_tx].width_narrow = tx_data['width_narrow']
            transmitters[current_tx].width_wide = tx_data['width_wide']
        
        return transmitters
    except FileNotFoundError:
        print("Data file not found.")
        return {}
    except Exception as e:
        print(f"Error loading state: {e}")
        return {}

def logState(transmitters, tx_name):

    with open(logfile, "a") as f:
        f.write(f"\n--- Initial values for {tx_name} ---\n")
        tx = transmitters[tx_name]
        f.write(f"Current DDM: {tx.current_DDM}\n")
        f.write(f"Current PSB: {tx.current_Psb}\n")
        f.write(f"Required course width: {tx.required_course_width}\n")
        f.write(f"Width narrow: {tx.width_narrow}\n")
        f.write(f"Width wide: {tx.width_wide}\n")
        f.write(f"Clearance 90: {tx.clearance_90}\n")
        f.write(f"Clearance 150: {tx.clearance_150}\n")
        f.write(f"CLDDM 90: {tx.clddm_90}\n")
        f.write(f"CLDDM 150: {tx.clddm_150}\n")
        f.write("--------------\n")

def changeCourseWidth(transmitter: Transmitter, negative: bool, transmitters):
    if negative:
        print(f"Specification value @ 18% is {transmitter.width_wide} dbm\n")
    else:
        print(f"Specification value @ 18% is {transmitter.width_narrow} dbm\n")
    while True:
        user_input = input('Enter any value (percentage) between 5 to 20, "exit" to exit\n')
        if user_input.lower() == "exit":
            break
        try:
            percentValue = round(float(user_input) / 100, 3)
            math.log10(percentValue)
        except ValueError:
            print("Value should be non-negative")
            continue
        
        increaseValue = 1 + percentValue
        with open(logfile, "a") as f:
            if negative:
                f.write(f"{datetime.now().time().replace(microsecond=0)} Course width wide PSB is {transmitter.width_narrow}, change is {user_input}%, new PSB is {transmitter.current_Psb - 20 * math.log10(increaseValue)}\n")
            else:
                f.write(f"{datetime.now().time().replace(microsecond=0)} Course width narrow PSB is {transmitter.width_narrow}, change is {user_input}%, new PSB is {transmitter.current_Psb + 20 * math.log10(increaseValue)}\n")
        
        if negative:
            transmitter.width_wide = transmitter.current_Psb - 20 * math.log10(increaseValue)
        else:
            transmitter.width_narrow = transmitter.current_Psb + 20 * math.log10(increaseValue)
        
        transmitter.width_narrow = round(transmitter.width_narrow, 3)
        transmitter.width_wide = round(transmitter.width_wide, 3)
        
        saveStateToFile(transmitters)
        
        if negative:
            print(f"NEW COURSE WIDTH WIDE PSB IS {transmitter.width_wide}, type \"exit\" to exit\n")
        else:
            print(f"NEW COURSE WIDTH NARROW PSB IS {transmitter.width_narrow}, type \"exit\" to exit\n")

def printTable(transmitter: Transmitter):
    print("The list of values are:")
    print(f"{'Feet':<6} {'Microamps':>10}")
    if transmitter.category == 1:
        for feet, microamps in dataClddmCat1:
            print(f"{feet:<6}' {microamps:>10.2f}")
    elif transmitter.category == 2:
        for feet, microamps in dataClddmCat2:
            print(f"{feet:<6} {microamps:>10.2f}")
    else:
        for feet, microamps in dataClddmCat3:
            print(f"{feet:<6}' {microamps:>10.2f}")

def modifyClddm90(transmitter: Transmitter, transmitters):
    while True:
        printTable(transmitter)
        user_input = input('Enter new value of clddm 90, type "exit" to exit\n')
        if user_input.lower() == "exit":
            break
        try:
            new_clddm_90 = round(float(user_input), 3)
        except ValueError:
            print("Value should be numeric")
            continue
        
        with open(logfile, "a") as f:
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_90 is {transmitter.clddm_90} microAmps, new CL_DDM_90 is {new_clddm_90} microAmps\n")
        
        transmitter.clddm_90 = round(new_clddm_90, 3)
        saveStateToFile(transmitters)
        print(f"NEW CL_DDM_90 IS {transmitter.clddm_90}μA ({round(transmitter.current_DDM * 0.1033, 3)}%)")

def modifyClddm150(transmitter: Transmitter, transmitters):
    while True:
        printTable(transmitter)
        user_input = input('Enter new value of cl_ddm_150, type "exit" to exit\n')
        if user_input.lower() == "exit":
            break
        try:
            new_clddm_150 = round(float(user_input), 3)
        except ValueError:
            print("Value should be numeric")
            continue
        
        with open(logfile, "a") as f:
            f.write(f"{datetime.now().time().replace(microsecond=0)} current CL_DDM_150 is {transmitter.clddm_150} microAmps, new CL_DDM_150 is {new_clddm_150} microAmps\n")
        
        transmitter.clddm_150 = round(new_clddm_150, 3)
        saveStateToFile(transmitters)
        print(f"NEW CL_DDM_150 IS {transmitter.clddm_150}μA ({round(transmitter.clddm_150 * 0.1033, 3)}%)")

def modifyClddm(transmitter: Transmitter, transmitters):
    while True:
        user_input = input('Enter Delta value (μA) (FIU): ')
        if user_input.lower() == "exit":
            break
        try:
            delta = round(float(user_input), 3)
        except ValueError:
            print("Delta should be numeric")
            continue
        
        with open(logfile, "a") as f:
            f.write(f"{datetime.now().time().replace(microsecond=0)} current DDM value is{transmitter.current_DDM} microAmps, delta is {delta} microAmps, new DDM is {delta + transmitter.current_DDM} microAmps\n")
        
        transmitter.current_DDM = delta + transmitter.current_DDM
        transmitter.current_DDM = round(transmitter.current_DDM, 3)
        saveStateToFile(transmitters)
        print(f"NEW DDM IS {transmitter.current_DDM}μA ({round(transmitter.current_DDM * 0.1033, 3)}%), type \"exit\" to exit")

def modifyPsb(transmitter: Transmitter, transmitters):
    while True:
        user_input = input('Enter course width value (in degrees) (FIU): ')
        if user_input.lower() == "exit":
            break
        try:
            course_width_FIU = round(float(user_input), 3)
            math.log10(course_width_FIU)
        except ValueError:
            print("Course width should be numeric and non-negative")
            continue
        
        with open(logfile, "a") as f:
            f.write(f"{datetime.now().time().replace(microsecond=0)} CurrentPSB is {transmitter.current_Psb}, delta is {course_width_FIU}, new PSB is {transmitter.current_Psb + 20 * math.log10(course_width_FIU / transmitter.required_course_width)}\n")
        
        transmitter.current_Psb = transmitter.current_Psb + 20 * math.log10(course_width_FIU / transmitter.required_course_width)
        transmitter.current_Psb = round(transmitter.current_Psb, 3)
        saveStateToFile(transmitters)
        print(f"NEW PSB IS {transmitter.current_Psb}, type \"exit\" to exit\n")

# Main program
print("Restore previous values? (y/n)")
restore = input().lower()
transmitters = {}
if restore == 'y':
    transmitters = loadStateFromFile()
    if transmitters:
        print("\nRestored successfully!")
    else:
        print("Could not restore, enter new values.")
        restore = 'n'

if restore == 'n' or not transmitters:
    print("Enter category (1 or 2 or 3)")
    while True:
        try:
            category = int(input())
            break
        except ValueError:
            print("Category must be between 1 to 3")

    print("Enter required course width")
    while True:
        try:
            reqCourseWidth = round(float(input()), 3)
            break
        except ValueError:
            print("Course width must be numeric")

    for a in range(1, 3):
        print(f"\n=== Initializing values for Tx{a} ===")
        while True:
            try:
                clddm = round(float(input("Enter CL_DDM (μA): ")), 3)
                break
            except ValueError:
                print("Error: CL_DDM must be a numeric value")
        
        while True:
            try:
                psb = round(float(input("Enter PSB (dBm): ")), 3)
                if psb <= 0:
                    print("Error: PSB must be positive")
                    continue
                break
            except ValueError:
                print("Error: PSB must be a numeric value")

        while True:
            try:
                clearance_90 = round(float(input("Enter clearance 90 (μA): ")), 3)
                if clearance_90 <= 0:
                    print("Error: Clearance must be positive")
                    continue
                break
            except ValueError:
                print("Error: Clearance must be a numeric value")

        while True:
            try:
                clearance_150 = round(float(input("Enter clearance 150 (μA): ")), 3)
                if clearance_150 <= 0:
                    print("Error: Clearance must be positive")
                    continue
                break
            except ValueError:
                print("Error: Clearance must be a numeric value")
        
        transmitters[f"transmitter{a}"] = Transmitter(clddm, psb, category, reqCourseWidth, clearance_90, clearance_150)
        print(f"\nTx{a} initialized successfully!")
        logState(transmitters, f"transmitter{a}")
    
    saveStateToFile(transmitters)

tx1 = transmitters["transmitter1"]
tx2 = transmitters["transmitter2"]

# Main loop
while True:
    print(f"\n    Parameter       Current Value"
        f"\n1.  Tx1 cl_ddm         {tx1.current_DDM} μA\n"
        f"2.  Tx1 psb            {tx1.current_Psb} dBm\n"
        f"3.  Tx1 cl_ddm_90      {tx1.clddm_90} μA\n"
        f"4.  Tx1 cl_ddm_150     {tx1.clddm_150} μA\n"
        f"5.  Tx1 width_narrow   {tx1.width_narrow:.3f} dBm\n"
        f"6.  Tx1 width_wide     {tx1.width_wide:.3f} dBm\n"
        f"7.  Tx2 cl_ddm         {tx2.current_DDM} μA\n"
        f"8.  Tx2 psb            {tx2.current_Psb} dBm\n"
        f"9.  Tx2 cl_ddm_90      {tx2.clddm_90} μA\n"
        f"10. Tx2 cl_ddm_150     {tx2.clddm_150} μA\n"
        f"11. Tx2 width_narrow   {tx2.width_narrow:.3f} dBm\n"
        f"12. Tx2 width_wide     {tx2.width_wide:.3f} dBm\n"
        f"\nSelect parameter number to modify from the above menu:\n"
    )

    while True:
        try:
            choice = int(input())
            break
        except ValueError:
            print("Choice must be a number between 1-12")

    match choice:
        case 1:
            print(f"Modifying cl_ddm Tx1, current value is {tx1.current_DDM}")
            modifyClddm(tx1, transmitters)
        case 2:
            print(f"Modifying psb Tx1, current value is {tx1.current_Psb}")
            modifyPsb(tx1, transmitters)
        case 3:
            print(f"Modifying cl_ddm_90, Tx1 current value is {tx1.clddm_90}")
            modifyClddm90(tx1, transmitters)
        case 4:
            print(f"Modifying cl_ddm_150, Tx1, current value is {tx1.clddm_150}")
            modifyClddm150(tx1, transmitters)
        case 5:
            changeCourseWidth(tx1, False, transmitters)
        case 6:
            changeCourseWidth(tx1, True, transmitters)
        case 7:
            print(f"Modifying cl_ddm Tx2, current value is {tx2.current_DDM}")
            modifyClddm(tx2, transmitters)
        case 8:
            print(f"Modifying psb Tx2, current value is {tx2.current_Psb}")
            modifyPsb(tx2, transmitters)
        case 9:
            print(f"Modifying cl_ddm_90 Tx2, current value is {tx2.clddm_90}")
            modifyClddm90(tx2, transmitters)
        case 10:
            print(f"Modifying cl_ddm_150 Tx2, current value is {tx2.clddm_150}")
            modifyClddm150(tx2, transmitters)
        case 11:
            changeCourseWidth(tx2, False, transmitters)
        case 12:
            changeCourseWidth(tx2, True, transmitters)
        case _:
            print("Invalid choice")