import sys
sys.path.insert(1, "/home/orin/jetbot/")
 

from jetbot import Robot
import jetson_utils

# NanoOWL
from nanoowl.owl_predictor import (OwlPredictor)
from nanoowl.owl_drawing import (draw_owl_output)

from PIL import Image  # Pillow import

import numpy as np

robot = Robot()

# Change CSI Source as needed 
camera = jetson_utils.videoSource("csi://0", argv=sys.argv)
image = camera.Capture()
jetson_utils.cudaDeviceSynchronize()

# If you wish to change the model, you can, but this is the default upon creating a instance of class OwlPredictor
model = "google/owlvit-base-patch32"
image_encoder_engine = "/home/orin/nanoowl/data/owl_image_encoder_patch32.engine"
predictor = OwlPredictor(model, image_encoder_engine=image_encoder_engine)

# Gets prompt and then searches for detections
texts = "[a stop sign, a can]"
threshold = 0.1
texts = texts.strip("][()")
text = texts.split(',')
print(text)
images = Image.fromarray(np.uint8(image.value))
text_encodings = predictor.encode_text(text)
detections = predictor.predict(image=images, text=text, text_encodings=text_encodings, threshold=threshold, pad_square=False)
print("detections: ", detections)

