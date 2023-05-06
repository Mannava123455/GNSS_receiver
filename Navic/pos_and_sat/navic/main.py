import numpy as np
import math
import random


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


subframe_1=[random.randint(0, 1) for _ in range(292)]
subframe_2=[random.randint(0, 1) for _ in range(292)]
subframe_3=[random.randint(0, 1) for _ in range(292)]
subframe_4=[random.randint(0, 1) for _ in range(292)]

TLM_1=subframe_1[0:8]
TOWC_1=subframe_1[8:25]
Alert_1=subframe_1[25:26]
AUTONAV_1=subframe_1[26:27]
subframe_id_1=subframe_1[27:29]
spare_1=subframe_1[29:30]
DATA_1=subframe_1[30:262]
CRC_1=subframe_1[262:286]
Tail_1=subframe_1[286:292]
TLM_2=subframe_2[0:8]
TOWC_2=subframe_2[8:25]
Alert_2=subframe_2[25:26]
AUTONAV_2=subframe_2[26:27]
subframe_id_2=subframe_2[27:29]
spare_2=subframe_2[29:30]
DATA_2=subframe_2[30:262]
CRC_2=subframe_2[262:286]
Tail_2=subframe_2[286:292]
TLM_3=subframe_3[0:8]
TOWC_3=subframe_3[8:25]
Alert_3=subframe_3[25:26]
AUTONAV_3=subframe_3[26:27]
subframe_id_3=subframe_3[27:29]
spare_3=subframe_3[29:30]
Message_id_3=subframe_3[30:36]
DATA_3=subframe_3[36:256]
PRN_ID_3=subframe_3[256:262]
CRC_3=subframe_3[262:286]
Tail_3=subframe_3[286:292]
TLM_4=subframe_4[0:8]
TOWC_4=subframe_4[8:25]
Alert_4=subframe_4[25:26]
AUTONAV_4=subframe_4[26:27]
subframe_id_4=subframe_4[27:29]
spare_4=subframe_3[29:30]
Message_id_4=subframe_4[30:36]
DATA_4=subframe_4[36:256]
PRN_ID_4=subframe_4[256:262]
CRC_4=subframe_4[262:286]
Tail_4=subframe_4[286:292]
#subframe 1 data 
WN  = subframe_1[30:40]
af0 = subframe_1[40:62]
af1 = subframe_1[62:78]
af2 = subframe_1[78:86]
URA = subframe_1[86:90]
toc = subframe_1[90:106]
Tgd = subframe_1[106:114]
delta_n = subframe_1[114:136]
IODEC = subframe_1[136:144]
res = subframe_1[144:154]
l5_flag = subframe_1[154:155]
s_flag = subframe_1[155:156]
Cuc = subframe_1[156:171]
Cus = subframe_1[171:186]
Cic = subframe_1[186:201]
Cis = subframe_1[201:216]
Crc = subframe_1[216:231]
Crs = subframe_1[231:246]
IDOT= subframe_1[246:260]
spare = subframe_1[260:262]
print(subframe_1[246:260])
#subframe 2 data
M0  = subframe_2[30:62]
toe = subframe_2[62:78]
e   = subframe_2[78:110]
sqrtA=subframe_2[110:142]
omega_0=subframe_2[142:174]
omega=subframe_2[174:206]
omega_dot=subframe_2[206:228]
i0=subframe_2[228:260]
spare=subframe_2[260:262]
WN        =      decimal_to_binary(2163,10,0)
af0       =     decimal_to_binary(0.0007623047567904,22,-31)
af1       =     decimal_to_binary(-2.773958840407E-11,16,-43)
af2       =     decimal_to_binary(0,8,-55)
URA       =     decimal_to_binary(2,4,0)
toc       =     decimal_to_binary(0,16,16)
Tgd       =     decimal_to_binary(-1.862645E-09,8,-31)
delta_n   =     decimal_to_binary(3.171560679661E-09,22,-41)
IODEC     =     decimal_to_binary(0,8,1)
Cuc       =     decimal_to_binary(6.549060344696E-06,15,-28)
Cus       =     decimal_to_binary(2.816319465637E-05,15,-28)
Cic       =     decimal_to_binary(5.215406417847E-08,15,-28)
Cis       =     decimal_to_binary(2.756714820862E-07,15,-28)
Crc       =     decimal_to_binary(-770.75,15,-28)
Crs       =     decimal_to_binary(206.0625,15,-28)
IDOT      =     decimal_to_binary(1.361485282755E-09,14,-43)
M0        =     decimal_to_binary(0.7512157000178,32,-31)
toe       =     decimal_to_binary(345600,16,16)
e         =     decimal_to_binary(0.001829810556956,32,-33)
sqrtA     =     decimal_to_binary(6493.503732681,32,-19)
omega_0   =     decimal_to_binary(-2.882886621674,32,-31)
omega     =     decimal_to_binary(-3.120650200087,32,-31)
omega_dot =     decimal_to_binary(-2.738685505816E-09,22,-41)
i0        =     decimal_to_binary(0.5082782060675,32,-31)

frame=subframe_1+subframe_2+subframe_3+subframe_4


BDTWeek          =     binary_to_decimal( WN,10,0)
SVclockBias     =     binary_to_decimal(af0,22,-31)
SVclockDrift    =     binary_to_decimal(af1,16,-43)
SVclockDriftRate=     binary_to_decimal(af2,8 ,-55)
URA      =     binary_to_decimal(URA,4 ,0)
toc      =     binary_to_decimal(toc,16,16)
TGD      =     binary_to_decimal(Tgd,8 ,-31)
DeltaN  =     binary_to_decimal(delta_n,22,-41)
IODEC    =     binary_to_decimal(IODEC,8,1)
Cuc      =     binary_to_decimal(Cuc,15,-28)
Cus      =     binary_to_decimal(Cus,15,-28)
Cic      =     binary_to_decimal(Cic,15,-28)
Cis      =     binary_to_decimal(Cis,15,-28)
Crc      =     binary_to_decimal(Crc,15,-28)
Crs      =     binary_to_decimal(Crs,15,-28)
IDOT1    =     binary_to_decimal(IDOT,14,-43)
M0       =     binary_to_decimal(M0,32,-31)
Toe      =     binary_to_decimal(toe,16,16)
Eccentricity       =     binary_to_decimal(e,32,-33)
sqrtA    =     binary_to_decimal(sqrtA,32,-19)
Omega0   =     binary_to_decimal(omega_0,32,-31)
omega    =     binary_to_decimal(omega ,32,-31)
OmegaDot =     binary_to_decimal(omega_dot,22,-41)
Io       =     binary_to_decimal(i0,32,-31)
sv=0
time=0
month=0
day=0
hour=0
minute=0
second=0
codesL2=0
L2flag=0
health=0
TransTime=0
IODC=0


data = [sv,time,month,day,hour,minute,second,SVclockBias,SVclockDrift,SVclockDriftRate,IODEC,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT1,codesL2,BDTWeek,L2flag,URA,health,TGD,IODC,TransTime]

print(data)
