## Jetbot with Jetson Orin Nano

Software setup for Jetbot using the Jetson Orin Nano
## How to Build & Install

Follow the documentation inside the presentations folder, then the following
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
### Object Detection
Run the track with
```
cd ~/jetbot/detect
sudo python3 rf-signs-updated-single-cam.py --flip-method=rotate-180
```
With Car Detection (on track)
```
cd ~/jetbot/detect
sudo python3 carfollowing.py
```

### Data Collection
Whether you need "--flip-method=rotate-180" may depends on the orientation of your camera.
```
cd ~/jetbot/data-collection
sudo python3 image-capture-single.py --flip-method=rotate-180
```
You can use other scripts inside the folder for other methods of capturing videos or images.

### Testing Folder
All code in this folder is still being developed, but is significant for further development for the Jetson Orin Nano.

NanoOWL
Follow these instructions to be able to run NanoOWL libraries referenced.
```
cd~
git clone https://github.com/NVIDIA-AI-IOT/nanoowl 
pip install pillow
```
Multi-Detect
This code is a carbon copy of another code, however, is made for testing multiple cameras running different models. It is suggested to editing this code for all test-cases for multi-camera autonomous driving using models.

### Credits

Credit to Stephen Qiu and Franklin Zhang for their contributions.
