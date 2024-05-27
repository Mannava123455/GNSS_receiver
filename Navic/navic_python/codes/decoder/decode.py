import numpy as np
from sk_dsp_comm import fec_conv as fec
from sk_dsp_comm import digitalcom as dc

#inp = np.random.randint(2,size=292)
inp = np.ones(292)
print (inp)
state ='000000'
cc1 = fec.FECConv(('1011011','1111001'))
out,state = cc1.conv_encoder(inp,state)  

# Perform Viterbi decoding using the dc.viterbi_decode function from sk_dsp_comm

y = np.array(out).astype(int)
z = cc1.viterbi_decoder(y,'hard')
print (z ,len(z))

# Compare the original input with the decoded output
print(np.array_equal(inp, z))
