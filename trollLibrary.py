
from random import randint
boll = False
while True:
    print("\nGet access ID: ",randint(0,100))

    print("\n LoginID:      ",randint(0,1000000)*(0.001),)
    print("\n   Senha:      ",randint(100000,999999))

    a = randint(0,100000)
    if a >= 99999:
        boll = True
    else:
        boll = False
    print("\n TryAccess:    ",boll)



    if(boll):
        print("Access Granted for last ID")
        print("Exiting")
        quit()
