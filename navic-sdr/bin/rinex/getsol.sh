#!/usr/bin/bash

navfile="ignss-sdrlib.nav"
obsfile="ignss-sdrlib.obs"

clearfiles () {
    tput setaf 7
    rm $navfile 2>/dev/null
    exit 0
}

trap clearfiles 2

navMinSat=5
navHeaderLineCnt=3
navRecordLineCnt=8
navMinLineCnt=$(($navHeaderLineCnt + $navMinSat * $navRecordLineCnt))

navLineCnt=$(wc -l $navfile 2>/dev/null | cut -d' ' -f1)
while [[ $navLineCnt -lt $navMinLineCnt ]]
do
    echo "Waiting for Navigation Data...."
    sleep 1
    navLineCnt=$(wc -l $navfile 2>/dev/null | cut -d' ' -f1)
done
echo "Navigation Data Received!"

echo "Starting Position Fix"
tput setaf 2
echo $(./rnx2rtkp -p 2 -f 1 -t -s , -l 0.0 0.0 0.0 $obsfile $navfile | head -n 9 | tail -n 1 | cut -d',' -f1-5)

tput setaf 6
re='^[0-9]+$'
obsPrevModTime=0
obsCurrentModTime=$(stat -c '%Y' $obsfile)
while test $(($obsCurrentModTime - $obsPrevModTime)) -ne 0
do
    fixline=$(./rnx2rtkp -p 2 -f 1 -t -s , -l 0.0 0.0 0.0 $obsfile $navfile | tail -n 1)
    fixstat=$(echo $fixline | cut -d',' -f5)
    if ! [[ $fixstat =~ $re ]]
    then
        if [[ $fixstat -eq 5 ]]
        then 
            echo $(echo $fixline | cut -d',' -f1-4)
        fi
    fi
    sleep 1
    obsPrevModTime=$obsCurrentModTime
    obsCurrentModTime=$(stat -c '%Y' $obsfile)
done  

tput setaf 7
rm $navfile
