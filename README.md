# Vex-AI-2021-Code

Setting up ssh on the vex administered jetson: sudo nano /etc/NetworkManager/NetworkManager.conf then change managed=false to managed=true sudo service network-manager restart then connect to wifi, safe ip, and ssh.


Clone repository
Put copy runs folder from google drive into the yolov5 folder
run detectVexai.py from WITHIN the yolov5 folder
you may have to tweak the camera parameter

(this model was trained on a small dataset for a very limited time period, so take all results with a grain of salt)
