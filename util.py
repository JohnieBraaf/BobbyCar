
BIT= int(16)

# Convert a hex number (in 2's negate) to Decmal
def toDec(hexstr):
    msb4bits = hexstr[0]
    n = int(msb4bits, 16)
    if n >= 8:
        p = -1*pow(2,BIT-1)
        addend = int(str(n-8) + hexstr[1:], 16)
        return str( p + addend)
    else:
        return str(int(hexstr, 16))    
            

# Convert a decimal number to  2's negate Hex
def toHex(n):

    num = int(n)
    if num == 0: 
        return '0000'
    
    M = '0123456789abcdef'  # like a map
    ans = ''

    chunks = int(BIT) / int(4)
    
    for i in range(chunks):
        n = num & 15       # this means num & 1111b
        c = M[n]          # get the hex char 
        ans = c + ans
        num = num >> 4

    return ans 
