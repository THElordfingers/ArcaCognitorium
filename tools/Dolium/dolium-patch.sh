#!/bin/bash
#
##
###
#####
######## dolium-patch.sh

echo "Unzipping dolizum.zip..."
unzip dolium.zip

sleep 0.5

echo "Moving contents of /dolium ..."
cd ~/Dolium/dolium/
mv * ~/Dolium/

sleep 0.5 

echo "Moving contents of /dolium/ui ..."

cd ~/Dolium/dolium/ui/
mv * ~/Dolium/ui/

sleep 0.5 

echo "Removing Unecessaries..."
cd ~/Dolium/
rm -r dolium
rm dolium.zip

sleep 0.5

echo "done!"
