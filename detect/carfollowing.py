import sys
sys.path.insert(1, '/home/orin/jetbot/')

import jetson_inference
import jetson_utils
import argparse

import torch
from torch2trt import TRTModule
import torchvision.transforms as transforms
import torch.nn.functional as F

import cv2
import PIL.Image
import numpy as np

import os
import keyboard
import time
import datetime
import inputs
import threading

from operator import attrgetter

from jetbot import Robot
#from robot_gpio import Robot
#robot = Robot(left_multiplier=0.95)
robot = Robot()

speed_adjustment = 2
slow_speed = 0.15
fast_speed = 0.25

def fractional_coord(bbox, dir, frac):
    """Find location that's a fraction of the way right/down the bounding box"""
    if dir == "x":
        return bbox.Left + frac * (bbox.Right - bbox.Left)
    elif dir == "y":
        return bbox.Top + frac * (bbox.Bottom - bbox.Top)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Classify a live camera stream using an image recognition DNN.",
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        epilog=jetson_inference.imageNet.Usage() +
                                                jetson_utils.videoSource.Usage() + jetson_utils.videoOutput.Usage() + jetson_utils.logUsage())
    parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
    parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
    parser.add_argument("--network", type=str, default="resnet18",
                        help="pre-trained model to load (see below for options)")
    parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
    parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
    parser.add_argument("--camera", type=str, default="0",
                        help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
    parser.add_argument("--width", type=int, default=640, help="desired width of camera stream (default is 1280 pixels)")
    parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")
    parser.add_argument('--headless', action='store_true', default=(), help="run without display")

    # For rtp streaming
    is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]
    
    try:
        opt = parser.parse_known_args()[0]
    except:
        print("")
        parser.print_help()
        sys.exit(0)

    # load the recognition network (object detection models)
    # intersection_net = jetson_inference.detectNet(argv=['--model=/home/orin/jetbot/models/intersect.onnx', '--labels=/home/orin/jetbot/models/intersection-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes', '--threshold=0.3'])
    #sign_net = jetson_inference.detectNet(argv=['--threshold=0.8', '--model=/home/orin/jetbot/models/full-signs.onnx', '--labels=/home/orin/jetbot/models/sign-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
    #line_net = jetson_inference.detectNet(argv=['--threshold=0.2', '--model=/home/orin/jetbot/models/orange-green-lines.onnx', '--labels=/home/orin/jetbot/models/orange-green-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
    car_net = jetson_inference.detectNet(argv=['--threshold=0.8', '--model=/home/orin/jetbot/models/carModel.onnx', '--labels=/home/orin/jetbot/models/carLabels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
   
    # create video sources & outputs
    camera1 = jetson_utils.videoSource("csi://0", argv=sys.argv)

    #display = jetson_utils.videoOutput("display://0", argv=sys.argv + is_headless)

    #### ADJUST IP ADDRESS to match the laptop's here
    display = jetson_utils.videoOutput("rtp://10.131.132.162:1234", argv=sys.argv + is_headless)

    font = jetson_utils.cudaFont()
    
    # Robot starts to find a car to follow
    state = "finding_car"
    left = False
    
    while True:
        # capture the next image
        image1 = camera1.Capture()
        img_area = image1.width * image1.height
        
        #detect the car
        cars = car_net.Detect(image1, overlay=opt.overlay)
        if len(cars) == 0:
            state = "finding_car"
        else:
            state = "following_car"
        
        if state == "finding_car":
            print("finding car")
            if left:
                # turn left a little bit
                print("finding left")
                robot.set_motors(slow_speed * speed_adjustment, fast_speed * speed_adjustment)
                time.sleep(0.2)
            else:
                # turn right a little bit
                print("finding right")
                robot.set_motors(fast_speed * speed_adjustment, slow_speed * speed_adjustment)
                time.sleep(0.2)
        
        elif state == "following_car":
            for car in cars:
                #if the car is close
                if car.Area > img_area/4:
                    print("too close")
                    robot.stop()
                    break
                elif car.Area < img_area/20:
                    print("speeding up")
                    slow_speed = 0.3
                    fast_speed = 0.5
                else:
                    slow_speed = 0.15
                    fast_speed = 0.25
                    
                #if the car if not close  
                #if the car is in the center of the image
                #avg left and right?
                #elif car.Left/image1.width == car.Right/image1.width:                
                #    print("center")
                #    robot.set_motors(0.2 * speed_adjustment, 0.2 * speed_adjustment)
                middle = (car.Left + car.Right) / 2

                #if the car is on the left hand side
                if middle < image1.width * 0.4:
                    print("left")
                    robot.set_motors(slow_speed * speed_adjustment, fast_speed * speed_adjustment)
                    time.sleep(0.2)
                    robot.set_motors(fast_speed * speed_adjustment, fast_speed * speed_adjustment)
                #if the car is on the right hand side
                elif middle > image1.width * 0.6:
                    print("right")
                    robot.set_motors(fast_speed * speed_adjustment, slow_speed * speed_adjustment)
                    time.sleep(0.2)
                    robot.set_motors(fast_speed * speed_adjustment, fast_speed * speed_adjustment)
                #if the car is in the center
                else:
                    print("center")
                    robot.set_motors(fast_speed * speed_adjustment, fast_speed * speed_adjustment)
                    
        #display the image
        #display.Render(image1)
        display.Render(image1)
        display.SetStatus("Object Detection | Network: {}".format(opt.network))
        
        # set the robot state
        if left:
            left = False
        else:
            left = True