echo "GPS samples are generating at the given location "
#./gps-sdr-sim -e brdc0010.22n  -s 2048000 -b 1 -d 40 -l 30,120,100
./gps-sdr-sim -e brdc0010.22n  -s 2048000 -b 1 -d 40 -l 60,100,50
#./gps-sdr-sim -e brdc0010.24n  -s 2048000 -b 1 -d 40 -l 10,20,100
#./gps-sdr-sim -e brdc0010.22n  -s 2048000 -b 1 -d 40 -l 16.29974,80.45729,100
#./gps-sdr-sim -e brdc0010.22n  -s 2048000 -b 1 -d 40 -l 25.6126,85.158875,100

gcc -o fsgps fsgps.c -lm

echo "GPS samples are generated at 1bit IQ "

gcc -o sample_buff_gen sample_buff_gen.c

./sample_buff_gen


echo "The IF is added to the I+Q samples  "

make

./fsgps -s 2048000 -i 1000000 iq_if.bin

