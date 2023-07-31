
import numpy as np
import math
import random
import numpy as np
import math
import random
import sys
import pandas as pd


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



def decimal_to_binary(n,bits,sf):
    m=abs(n)
    x=int(m/(2**(sf)))
    binary=d_2_b(x)
    if(len(binary)<bits):
        zeros=bits-len(binary)
        for i in range(zeros):
            binary.insert(0, 0)

    if(n>=0):
        return binary
    else:
        return twos_comp(binary)

def binary_to_decimal(bi,bits,sf):
    if(bi[0]==1):
        binary=twos_comp(bi)
        x=-1*(b_2_d(binary))*(2**(sf))
        return x
    else:
        binary=bi
        x=(b_2_d(binary))*(2**(sf))
        return x

def binary_to_decimal_non_comp(bi,bits,sf):
        binary=bi
        x=(b_2_d(binary))*(2**(sf))
        return x


def weeknum(weeknum,n):
    if(weeknum>1024):
        weeknum=weeknum-n*1024;
    return decimal_to_binary(weeknum,10,0)

def decode_week(w,n):
    x=binary_to_decimal(w,10,0)
    x=x+n*1024
    return x


s_1=[random.randint(0, 1) for _ in range(1168)]
s_2=[random.randint(0, 1) for _ in range(1168)]
s_3=[random.randint(0, 1) for _ in range(1168)]
s_4=[random.randint(0, 1) for _ in range(1168)]


frames = [[s_1], [s_2], [s_3], [s_4]]
print(frames)


data=[[1,2,3,4],[1,2,1,1],[1,2,3,4],[1,7,8,9]]

b = [[sublist[0][0:2] for sublist in frames]]
b=[[decimal_to_binary(sublist[0],2,0) for sublist in data]]
b= [item for sublist in b for item in sublist]

print()
print(b)
e=[]
for sublist in b:
    d=binary_to_decimal(sublist,2,0)
    e.append(d)
e=np.reshape(e,(-1,1)).tolist()
print(e)
