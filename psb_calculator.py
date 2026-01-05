from datetime import datetime
import math
logfile = "log.txt"

print("enter initial Psb(dbm)")
initial_Psb = float(input()) 

print("enter required course width")
required_course_width =float(input())

current_Psb = initial_Psb

with(open(logfile,"a") as f ):
    f.write(f"{datetime.now().date()} \nInitial Psb is {initial_Psb} and required course width is {required_course_width} \n")

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
        f.write(f"{datetime.now().time().replace(microsecond=0)} CurrentPSB is {current_Psb}, delta is {course_width_FIU}, new PSB is {current_Psb + 20 * math.log10(course_width_FIU/required_course_width)} \n")
    current_Psb = current_Psb + 20 * math.log10(course_width_FIU/required_course_width) 
    current_Psb = round(current_Psb,3)
    print(f"NEW PSB IS  ******* {current_Psb} ******, type \"exit\" to exit ",)

with(open(logfile,"a") as f ):
    f.write(f"{datetime.now().time().replace(microsecond=0)} Final PSB value is {current_Psb} \n")

print(f"Initial PSB value was {initial_Psb}")
print(f"Final PSB value is {current_Psb}")
