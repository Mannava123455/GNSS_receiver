# Project done under Dr.GVV Sharma Assoc Prof IITH

### Implemented the navic L5 receiver in a real time using SDR

### Requirements: 

#### Hardware:
1.USRP SDR

2.bladerf SDR

3.PC with 64 bit Linux os

#### software:

1.RTKlib

2.uhd(USRP application)


### specifications:

Receiver sampling frequency is at 2.048 Mhz


## Installations:

Install the configurations for bladerf and usrp from the https://github.com/Mannava123455/module_3/blob/main/Navic/installations.txt

## Transmiter

For generating the samples get the below folder

```
 svn co https://github.com/Mannava123455/module_3/trunk/Navic/navic_transmiter
```

```
 make
```

This command will generate bin file that contain the IQ samples of 300 sec with 16 bit  i.e in bin file 1st 16 bits is I and second 16 bits is Q and this flow will continous and this file will be for sdr implementation

```
 ./navic-sdr-sim -e brdc1380.23n -s 2048000 -l 30,120,100
```

For file input we have to use 8 bit duration i.e in bin file 1st 8 bits is I and second 8 bits is Q and this flow will continous
```
 ./navic-sdr-sim -e brdc1380.23n -s 2048000 -l 30,120,100 -b 8  

```
## Receiver

In order to run the navic reciver get the folder below

```
 svn co https://github.com/Mannava123455/module_3/trunk/Navic/navic_receiver
```
```
 cd navic_receiver/cli/linux
```

```
make
```
```
cd navic_receiver/bin
```

```
./ignss-sdrcli
```
