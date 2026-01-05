from datetime import datetime

logfile = "log.txt"
print("enter present CL_DDM(μA)")

clddm = float(input())
current_DDM = clddm
with(open(logfile,"a") as f ):
    f.write(f"{datetime.now().date()} \nInitial DDM is {current_DDM} \n")
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
        f.write(f"{datetime.now().time().replace(microsecond=0)} currentDDM is {current_DDM} microAmps, delta is {delta} microAmps, new DDM is {delta + current_DDM} microAmps \n")
    current_DDM = delta + current_DDM
    current_DDM = round(current_DDM,3)
    print(f"NEW DDM IS  ******* {current_DDM}μA ({round(current_DDM * 0.1033,3)} %) ******, type \"exit\" to exit ",)

with(open(logfile,"a") as f ):
    f.write(f"{datetime.now().time().replace(microsecond=0)} Final DDM value is {current_DDM} \n")
print(f"Initial DDM value was {clddm}μA ({round(clddm * 0.1033,3)}%)")
print(f"Final DDM value is {current_DDM}μA {round(current_DDM*0.1033,3)}%")
