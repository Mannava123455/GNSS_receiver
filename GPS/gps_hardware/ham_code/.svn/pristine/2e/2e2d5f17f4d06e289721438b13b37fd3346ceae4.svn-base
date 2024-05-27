echo "GPS samples are generating at the given location "
./gps-sdr-sim -e brdc0010.22n  -s 2048000 -b 1 -d 40 -l 17.5947,78.1230,100


echo "GPS samples are generated at 1bit IQ "

gcc -o sample_buff_gen sample_buff_gen.c

./sample_buff_gen


echo "The IF is added to the I+Q samples  "

make

./fsgps -s 2048000 -i 1000000 iq_if.bin

