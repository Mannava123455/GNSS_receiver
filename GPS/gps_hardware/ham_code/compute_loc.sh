./gps-sdr-sim -e brdc0010.22n  -s 5456000 -b 1 -d 77 -l 30,120,100


gcc -o sample_gen_if sample_gen_if.c

./sample_gen_if

make

./fsgps -s 5456000 -i 4092000 iq_if.bin

