## Jetbot with Jetson Orin Nano

Software setup for Jetbot using the Jetson Orin Nano

## How to Install

```
cd ~
git clone https://github.com/Syncron19/Jetbot-Orin.git
cd jetbot
./install.sh
source ~/.bashrc

# Installing Tensorflow (used with all models)
sh ./tf_install.sh   

```



### Testing
Test motors with:
```
cd ~/jetbot/jetbot
python3 motor_test.py
```
For camera testing:
- If the Jetson Nano is connected to a monitor, run

```
nvgstcapture-1.0
```
- Otherwise, to view the camera feed remotely, run the following with jetson-inference installed (replace ```IP``` with address of receiving device):

```video-viewer csi://0 rtp://IP:1234 --input-flip=rotate-180```

and run the following on the receiving device:
```
gst-launch-1.0 -v udpsrc port=1234 \
 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! \
 rtph264depay ! decodebin ! videoconvert ! autovideosink
```


### Running
Run the track with
```
cd ~/jetbot/src
sudo python3 rf-signs-updated.py --flip-method=rotate-180


```

### Data Collection
```
cd ~/jetbot/src/data-collection
sudo python3 image-capture-single.py --flip-method=rotate-180
```
Other options for data collection are also present - see the data-collection folder.

### Credits

Credit to Stephen Qiu and Franklin Zhang for their contributions.
