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

```nvgstcapture-1.0
```
### Running Detect Folder
Run the track with
```
cd ~/jetbot/detect
sudo python3 rf-signs-updated-single-cam.py --flip-method=rotate-180
```


### Data Collection
```
cd ~/jetbot/data-collection
sudo python3 image-capture-single.py --flip-method=rotate-180
```
You can use other scripts inside the folder for other methods of capturing videos or images.

### Credits

Credit to Stephen Qiu and Franklin Zhang for their contributions.
