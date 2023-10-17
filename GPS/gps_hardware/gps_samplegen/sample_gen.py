import numpy as np
# Function to convert a binary file to a list of 1s and 0s
def bin_to_list(bin_file):
    with open(bin_file, 'rb') as file:
        binary_data = file.read()
        binary_list = [int(bit) for byte in binary_data for bit in f'{byte:08b}']
    return binary_list

def list_to_bin(binary_list, bin_file):
    binary_data = bytearray()
    for i in range(0, len(binary_list), 8):
        byte_str = ''.join(map(str, binary_list[i:i+8]))
        byte = int(byte_str, 2)
        binary_data.append(byte)
    
    with open(bin_file, 'wb') as file:
        file.write(binary_data)


def list_to_little_endian(binary_list):
    little_endian_list = []
    for i in range(0, len(binary_list), 8):
        chunk = binary_list[i:i + 8]
        little_endian_list.extend(chunk[::-1])
    return little_endian_list


input_bin_file = 'gpssim.bin'
output_bin_file = 'out.bin'

binary_list = bin_to_list(input_bin_file)
#binary_list = binary_list[0:64]
#print(binary_list)
#np.savetxt("a.dat",binary_list)

I=binary_list[0::2]
Q=binary_list[1::2]

i=np.array(I)
q=np.array(Q)
data=i|q

little_endian_list = list_to_little_endian(data)



list_to_bin(little_endian_list, output_bin_file)

original_list = bin_to_list(input_bin_file)

restored_list = bin_to_list(output_bin_file)
#print(restored_list)
#np.savetxt("b.dat",restored_list)

if original_list == restored_list:
    print("The two lists are the same.")
else:
    print("The two lists are different.")
