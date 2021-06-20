# THE PROCESS
ssh nano@192.168.86.32  
cd Development/vexai8029_org/vexai8029_org   # this directory is used as a docker volume when the docker container is run 
git pull origin main  # get the most recent updates from this repo  
sudo docker run --gpus all -it --privileged -v /dev:/dev -v /home/nano/Development/vexai8029_org/vexai8029_org:/usr/shared-dev yolov5:rs  
# now you are in the docker container, run the following commands:  
pip3 install pyserial   # this will eventually be automatically run in the docker build process, but for now just manually install it  
cd /usr/yolov5  
python3 VexAiJetson.py #to launch file  


# Vex-AI-2021-Code

Setting up ssh on the vex administered jetson: sudo nano /etc/NetworkManager/NetworkManager.conf then change managed=false to managed=true sudo service network-manager restart then connect to wifi, safe ip, and ssh.


Clone repository
Put copy runs folder from google drive into the yolov5 folder  
run detectVexai.py from WITHIN the yolov5 folder  
you may have to tweak the camera parameter  
  
(this model was trained on a small dataset for a very limited time period, so take all results with a grain of salt)  


REQUIRED DEPENDANCIES FOR PYTORCH / TORCHVISION
#RUN apt install nvidia-cuda-toolkit  
#sudo apt-get install libavformat-dev  
#sudo apt-get install libavcodec-dev  
#sudo apt-get install libswscale-dev  
#sudo apt-get install libjpeg-dev  
#pip3 install pillow    
#pip3 install tqdm  
#pip3 install matplotlib  
#pip3 install pandas  
#pip3 install seaborn    
  
HOW TO DOWNLOAD FILES FROM GOOGLE DRIVE VIA COMMAND LINE  
sudo apt-get install unzip  
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id={YOURIDHERE}' -r -A 'uc*' -e robots=off -nd  
{YOURIDHERE} = digits in url after /d/  
ls -l to find the largest of the three created files  
mv uc?export=download&confirm=w3R-&id=19aByVTPC1xEMTIuDg7-h__tl2Iy-Bo5U~ runs.  zip  change the name to the appropriate name and filetype    
unzip runs.zip  
done  :)  

to run a dockercontainer on startup, use the docker --restart=always flag  

another option is to use systemd like this: https://askubuntu.com/questions/620930/how-do-i-autostart-docker-container-at-system-reboot  

more info (https://docs.docker.com/config/containers/start-containers-automatically/)  


