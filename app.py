from flask import Flask, request, jsonify
from imutils import face_utils
from skimage import io
from skimage.draw import polygon_perimeter
import numpy as np
import imutils
import dlib
import cv2
import time
import math
import base64


def calculate_mask_size(landmarks, delta_coin, coin_type):
		# all sizes are in mm
	coin_type = coin_type.lower()
	if coin_type == "penny":
		coin_size = 19.05
	elif coin_type == "nickel":
		coin_size = 21.21
	elif coin_type == "dime":
		coin_size = 17.91
	elif coin_type == "quarter":
		coin_size = 24.26
	elif coin_type == "onepeso":
		coin_size = 23.00
	elif coin_type == "fivepeso":
		coin_size = 25.00
	elif coin_type == "tenpeso":
		coin_size = 27.00
	else:
		print("[ERROR] Coin type not in database. Using 25.00mm as placeholder")
		coin_size = 25.00
	
	chin, nose = landmarks[8], landmarks[18]
	delta_x, delta_y = abs(chin[0] - nose[0]), abs(chin[1] - nose[1])
	delta_face = math.sqrt((delta_x ** 2) + (delta_y ** 2))
	face_size = delta_face / (delta_coin / coin_size)
	
	if face_size >= 90.00:
		bucket = "Large/Extra Large"
	else:
		bucket = "Small/Medium"
		
	return(face_size, bucket)



def coin_detector(image_path):
		# Load coin detector
	detector = dlib.simple_object_detector("models/coin_detector.svm")
	
		# Load target image
	image = io.imread(image_path)
		
		# Run detector on target file
	coins = detector(image)
	
	counter = 0
		# Print coordinates of bounding box, if desired
	for d in coins:
		#print("left, top, right, bottom:", 
		#      d.left(), d.top(), d.right(), d.bottom())
		counter = counter + 1
	if counter != 0:
		delta_coin = d.bottom() - d.top()
		return(delta_coin)
	else:
		print("Error: Coin not detected. Returning 20 as placeholder")
		return(20)



def landmark_predictor(image_path):

		# initialize dlib's face detector then create facial landmark predictor
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor("models/landmark_predictor.dat")

		# load the input image, resize it, and convert it to grayscale
	image = cv2.imread(image_path)
	assert not isinstance(image,type(None)), "Image could not be loaded by landmark predictor"
	image = imutils.resize(image, width=500)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# detect faces in the grayscale image
	rects = detector(gray, 1)

		# loop over the face detections
	for (i, rect) in enumerate(rects):
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to NumPy array
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)

			# convert dlib's rectangle to a OpenCV-style bounding box
			# [i.e., (x, y, w, h)], then draw the face bounding box
		(x, y, w, h) = face_utils.rect_to_bb(rect)
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

			# loop over the (x, y)-coordinates for the facial landmarks
			# and draw them on the image
		for (x, y) in shape:
			cv2.circle(image, (x, y), 1, (0, 0, 255), -1)

		# Display results, then save image to output folder
	cv2.imshow("Output", image)
	tl = time.localtime(time.time())
	year, month, day = str(tl[0]), str(tl[1]), str(tl[2])
	hour, minute, second = str(tl[3]), str(tl[4]), str(tl[5])
	fixed_time = (year + "_" + month + "_" + day + "_" + 
			hour + "_" + minute + "_" + second)
	
	image_name = "./output/" + str(fixed_time) + ".jpg"
	cv2.imwrite(image_name, image)
	
	return(shape)


app = Flask(__name__)

@app.route("/health")
def health():
	return "Success", 200

@app.route("/mask_size", methods=["POST"])
def mask_size():

	data = request.form.to_dict(flat=False)

	#return jsonify(data), 200

	try:
		with open("test.jpg", "wb") as fh:
		#fh.write(base64.decodebytes(data['image'][0]))
			fh.write(base64.b64decode(data['image'][0]))
		fh.close()
	except:
		return "Error in reading image", 400

	try:
		image_path = 'test.jpg'
		coin_type = data['coin'][0]

		#image_path = input("Path to image?")
		#coin_type = input("Coin type?")

		delta_coin = coin_detector(image_path)
		landmarks = landmark_predictor(image_path)
		face_size, bucket = calculate_mask_size(landmarks, delta_coin, coin_type)

		#print("Estimated size (converted): " + str(face_size) + "mm")
		#print("Recommended mask size: " + bucket)

		res = {'size' : bucket}

		return jsonify(res), 200

	except:
		return "Error in predicting size", 400

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)