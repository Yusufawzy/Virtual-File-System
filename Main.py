import ctgs,linked,Indexed
while(True):
    print('='*100)
    a=int(input("Enter number:\n1-Contiguous Allocation\n2-Linked Allocation\n3-Indexed Location\n"))
    if (a==1):ctgs.Start()
    elif a==2:linked.Start()
    elif a==3: Indexed.Start()