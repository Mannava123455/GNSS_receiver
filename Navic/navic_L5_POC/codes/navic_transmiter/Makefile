# Makefile for Linux etc.

.PHONY: all clean time
all: navic-sdr-sim

USE_L5_BAND=1
USE_L1_BAND=0
USE_S_BAND=0

SHELL=/bin/bash
CC=gcc
CFLAGS=-O3 -Wall -D_FILE_OFFSET_BITS=64 
ifdef USER_MOTION_SIZE
CFLAGS+=-DUSER_MOTION_SIZE=$(USER_MOTION_SIZE)
endif
LDFLAGS=-lm

ifeq ($(USE_L5_BAND), 1)
CFLAGS+=-DNAVIC_L5
endif

ifeq ($(USE_L1_BAND), 1)
CFLAGS+=-DNAVIC_L1
endif

ifeq ($(USE_S_BAND), 1)
CFLAGS+=-DNAVIC_S
endif

navic-sdr-sim: navicsim.o
	${CC} $< ${LDFLAGS} -o $@

navicsim.o: .user-motion-size navic.h

.user-motion-size: .FORCE
	@if [ -f .user-motion-size ]; then \
		if [ "`cat .user-motion-size`" != "$(USER_MOTION_SIZE)" ]; then \
			echo "Updating .user-motion-size"; \
			echo "$(USER_MOTION_SIZE)" >| .user-motion-size; \
		fi; \
	else \
		echo "$(USER_MOTION_SIZE)" > .user-motion-size; \
	fi;

clean:
	rm -f navicsim.o navic-sdr-sim *.bin .user-motion-size

time: navic-sdr-sim
	time ./navic-sdr-sim -e brdc3540.14n -u circle.csv -b 1
	time ./navic-sdr-sim -e brdc3540.14n -u circle.csv -b 8
	time ./navic-sdr-sim -e brdc3540.14n -u circle.csv -b 16

.FORCE:

YEAR?=$(shell date +"%Y")
Y=$(patsubst 20%,%,$(YEAR))
%.$(Y)n:
	wget -q ftp://cddis.gsfc.nasa.gov/gnss/data/daily/$(YEAR)/brdc/$@.Z -O $@.Z
	uncompress $@.Z
