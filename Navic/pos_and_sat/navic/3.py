import numpy as np
def twos_comp(binary_num):
    inverted_num = []
    for bit in binary_num:
        inverted_num.append(1 - bit)

    carry = 1
    for i in range(len(binary_num)-1, -1, -1):
        if carry == 0:
            break
        elif inverted_num[i] == 0:
            inverted_num[i] = 1
            carry = 0
        else:
            inverted_num[i] = 0

    return inverted_num


def d_2_b(decimal):
    binary = []
    while decimal > 0:
        remainder = decimal % 2
        binary.insert(0, remainder)
        decimal = decimal // 2
    return binary


def b_2_d(binary):
    decimal = 0
    for i in range(len(binary)):
        decimal += binary[i] * (2 ** (len(binary) - 1 - i))
    return decimal


def decimal_to_binary(n, bits, sf):
    m = abs(n)
    x = int(m/(2**(sf)))
    binary = d_2_b(x)
    if len(binary) < bits:
        zeros = bits - len(binary)
        for i in range(zeros):
            binary.insert(0, 0)

    if n >= 0:
        return binary
    else:
        return twos_comp(binary)


def binary_to_decimal(bi, bits, sf):
    if bi[0] == 1:
        binary = twos_comp(bi)
        x = -1*(b_2_d(binary))*(2**(sf))
        return x
    else:
        binary = bi
        x = (b_2_d(binary))*(2**(sf))
        return x


a = [[0,1],[0,0],[1,1]]
b=[]
for sublist in a:
    decimal = binary_to_decimal(sublist, 2, 0)
    b.append(decimal)
b = np.reshape(b, (-1, 1)).tolist()
print(b)

