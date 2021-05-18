import mask_size_functions as f
import argparse
import sys


# [TODO] 
# determine resolution minimum
# I/O configuration optimums


def main(argv):
	ap = argparse.ArgumentParser()
	
	ap.add_argument("-i", "--image", required=True,
		help="Path to target image")
		
	ap.add_argument("-c", "--coin", required=True,
		help="Type of coin")

	args = vars(ap.parse_args())
	image_path = args["image"]
	coin_type = args["coin"]

	#image_path = input("Path to image?")
	#coin_type = input("Coin type?")
	
	delta_coin = f.coin_detector(image_path)
	landmarks = f.landmark_predictor(image_path)
	face_size, bucket = f.calculate_mask_size(landmarks, delta_coin, coin_type)
	
	print("Estimated size (converted): " + str(face_size) + "mm")
	print("Recommended mask size: " + bucket)



if __name__ == "__main__":
	main(sys.argv)
