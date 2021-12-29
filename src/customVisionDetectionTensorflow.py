# The steps implemented in the object detection sample code: 
# 1. for an image of width and height being (w, h) pixels, resize image to (w', h'), where w/h = w'/h' and w' x h' = 262144
# 2. resize network input size to (w', h')
# 3. pass the image to network and do inference
# (4. if inference speed is too slow for you, try to make w' x h' smaller, which is defined with DEFAULT_INPUT_SIZE (in object_detection.py or ObjectDetection.cs))
"""Sample prediction script for TensorFlow 1.x."""
import sys
# import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import numpy as np
from PIL import Image
from customVisionDetection import CustomVisionDetection
import cv2

class CustomVisionDetectionTensorflow(CustomVisionDetection):
    """Object Detection class for TensorFlow"""

    def __init__(self, modelPath, labelsFilePath):
        # Load a TensorFlow model
        graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(modelPath, 'rb') as f:
            graph_def.ParseFromString(f.read())

        # Load labels
        with open(labelsFilePath, 'r') as f:
            labels = [l.strip() for l in f.readlines()]

        super(CustomVisionDetectionTensorflow, self).__init__(labels)
        self.graph = tf.Graph()
        with self.graph.as_default():
            input_data = tf.placeholder(tf.float32, [1, None, None, 3], name='Placeholder')
            tf.import_graph_def(graph_def, input_map={"Placeholder:0": input_data}, name="")

        self.sess = tf.Session(graph=self.graph)
        

    def predict(self, preprocessed_image):
        inputs = np.array(preprocessed_image, dtype=np.float)[:, :, (2, 1, 0)]  # RGB -> BGR

        output_tensor = self.sess.graph.get_tensor_by_name('model_outputs:0')
        outputs = self.sess.run(output_tensor, {'Placeholder:0': inputs[np.newaxis, ...]})
        return outputs[0]

    def show_predictions(self, img, predictions, minScore):
        h, w, _ = img.shape
        for pr in predictions:
            score = float(pr['probability'])
            bbox =  pr['boundingBox']
            if score > minScore:
                x = bbox['left'] * w
                y = bbox['top'] * h
                right = (bbox['left']+ bbox['width']) * w
                bottom = (bbox['top']+ bbox['height']) * h
                cv2.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)
                cv2.circle(img,(int((x + right)/2),int((y + bottom)/2)),2,(0,0,255),3)
        return img

    def get_prediction_center(self, img, prediction):
        h, w, _ = img.shape
        bbox =  prediction['boundingBox']
  
        x = bbox['left'] * w
        y = bbox['top'] * h
        right = (bbox['left']+ bbox['width']) * w
        bottom = (bbox['top']+ bbox['height']) * h

        return (int((x + right)/2),int((y + bottom)/2))
    
    def get_prediction_size(self, img, prediction):
        h, w, _ = img.shape
        bbox =  prediction['boundingBox']
        width = bbox['width'] * w
        height = bbox['height'] * h

        return int( width * height)


