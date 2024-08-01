import sys
sys.path.insert(1, "/home/orin/jetbot/")

import jetson_inference
import jetson_utils
import argparse
import numpy as np
import cv2 # will be useful if jetson_utils doesn't work with v4l2 camera (USB)
import os
import keyboard
import time
from operator import attrgetter

from jetbot import Robot
robot = Robot()




# Note: If you wish to run more than one model, you will have to use some sort of loop to change the model which the cameras are using to detect. Check lines 95-100

IP = "10.131.50.87"
max_speed = 1.0

def create_video_sources():
    """Create two video sources for the dual cameras."""
    camera1 = jetson_utils.videoSource("csi://0", argv=sys.argv)
    camera2 = jetson_utils.videoSource("csi://1", argv=sys.argv)
    camera3 = jetson_utils.videoSource("v4l2:///dev/video2", argv=sys.argv)
    return camera1, camera2,camera3


def process_frames(camera1, camera2,camera3):
    """Capture and return the frames from both cameras."""
    image1 = camera1.Capture()
    image2 = camera2.Capture()
    image3 = camera3.Capture()
    return image1, image2,image3


def sort_lines(lines, num_labels):
    """Sort lines by given labels into arrays
    lines: list of lines
    labels: list of labels"""

    sorted_lines = [[] for i in range(num_labels)]
    for rl in lines:
        sorted_lines[rl.ClassID - 1].append(rl)
    
    return tuple(sorted_lines)


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

    # load the recognition network (object detection models) / change as needed
    sign_net = jetson_inference.detectNet(argv=['--threshold=0.8', '--model=/home/orin/jetbot/models/full-signs.onnx', '--labels=/home/orin/jetbot/models/sign-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
    # rf_net = jetson_inference.detectNet(argv=['--model=/home/jetbot/jetbot/models-2/green-line.onnx', '--labels=/home/jetbot/jetbot/models-2/green-line-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
    line_net = jetson_inference.detectNet(argv=['--threshold=0.2', '--model=/home/orin/jetbot/models/orange-green-lines-100.onnx', '--labels=/home/orin/jetbot/models/orange-green-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )
    high_line_net = jetson_inference.detectNet(argv=['--threshold=0.3', '--model=/home/orin/jetbot/models/orange-green-lines-100.onnx', '--labels=/home/orin/jetbot/models/orange-green-labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'] )

    # create video sources & outputs
    camera1, camera2 = create_video_sources()

    #### ADJUST IP ADDRESS to match the laptop's here
    display = jetson_utils.videoOutput(f"rtp://{IP}:1234", argv=sys.argv + is_headless)
    display1 = jetson_utils.videoOutput(f"rtp://{IP}:1234", argv=sys.argv + is_headless)

    # process frames until the user exits
    while True:
        # capture the next image
        image1, image2,image3= process_frames(camera1,camera2,camera3)
        detections1 = sign_net.Detect(image1)
        detections2 = sign_net.Detect(image2)
        detections3 = sign_net.Detect(image3)
        # Sync and Display the images
        jetson_utils.cudaDeviceSynchronize()
                
        # render the image
        display.Render(image1)
        display1.Render(image2)
        display2.Render(image3)

    
        # exit on input/output end of stream
        if not camera1.IsStreaming() or not display.IsStreaming():
            break


