
while True:
    netstr = input('enter str: ')
    if not (netstr.isalnum() and 2 < len(netstr) < 16):
        netstr = 'wrong_format'
    print(netstr)