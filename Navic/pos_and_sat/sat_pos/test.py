import numpy as np
from fractions import Fraction

# CA code generation API

SV_L5 = {
   1: '1110100111',
   2: '0000100110',
   3: '1000110100',
   4: '0101110010',
   5: '1110110000',
   6: '0001101011',
   7: '0000010100',
   8: '0100110000',
   9: '0010011000',
  10: '1101100100',
  11: '0001001100',
  12: '1101111100',
  13: '1011010010',
  14: '0111101010',
   15: '0011101111',
   16: '0101111101',
   17: '1000110001',
   18: '0010101011',
   19: '1010010001',
   20: '0100101100',
   21: '0010001110',
   22: '0100100110',
   23: '1100001110',
   24: '1010111110',
  25: '1110010001',
  26: '1101101001',
  27: '0101000101',
  28: '0100001101',
}

def shift(register, feedback, output):
    """GPS Shift Register
    
    :param list feedback: which positions to use as feedback (1 indexed)
    :param list output: which positions are output (1 indexed)
    :returns output of shift register:
    
    """
    
    # calculate output
    out = [register[i-1] for i in output]
    if len(out) > 1:
        out = sum(out) % 2
    else:
        out = out[0]
        
    # modulo 2 add feedback
    fb = sum([register[i-1] for i in feedback]) % 2
    
    # shift to the right
    for i in reversed(range(len(register[1:]))):
        register[i+1] = register[i]
        
    # put feedback in position 1
    register[0] = fb
    
    return out

def genNavicCaCode(sv):
    """Build the CA code (PRN) for a given satellite ID
    
    :param int sv: satellite code (1-14 L5 band, 15-28 S band)
    :returns list: ca code for chosen satellite
    
    """
    # init registers
    G1 = [1 for i in range(10)]

    if(sv<1 or sv>28):
        print("Error: PRN ID out of bounds!")
        return None
    elif(sv<=28):
        G2 = [int(i) for i in [*SV_L5[sv]]]

    ca = [] # stuff output in here

    # create sequence
    codeLength = 1023
    for j in range(codeLength):
        g1 = shift(G1, [3,10], [10])
        g2 = shift(G2, [2,3,6,8,9,10], [10])
        ca.append((g1 + g2) % 2)

    # return C/A code!
    return np.array(ca)
y=int(input())
x = genNavicCaCode(y)
np.savetxt("x.txt",x);
print(x)

