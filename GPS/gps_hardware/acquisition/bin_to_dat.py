import numpy as np
def read_binary_file(file_path):
    bit_list = []

    with open(file_path, 'rb') as file:
        byte = file.read(1)
        while byte:
            # Convert the byte to a binary string representation
            binary_str = bin(int.from_bytes(byte, byteorder='big'))[2:].zfill(8)
            
            # Iterate through each bit in the binary string and add it to the list
            for bit in binary_str:
                bit_list.append(int(bit))
            
            byte = file.read(1)

    return bit_list

# Example usage:
file_path = 'gpssim.bin'
bits = read_binary_file(file_path)
#bits=np.fromfile(file_path,np.int8)
np.savetxt("bin.dat",bits)
#I=bits[0::2]
#Q=bits[1::2]
#i=np.array(I)
#q=np.array(Q)
#
#data=i|q
#
#np.savetxt("data.dat",data)
#
#
## Print the list of bits
#np.savetxt("i.dat",I)
#np.savetxt("q.dat",Q)

