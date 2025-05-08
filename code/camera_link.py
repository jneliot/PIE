import cv2

camera_index = 0

def get_photo():
	cam = cv2.VideoCapture(camera_index)
	k = 0
	while True:
		ret, image = cam.read()
		if cam.isOpened():
			cv2.imshow('Image_Goutte.jpg',image)
			k = cv2.waitKey(1)
			
		if k != -1:
			break
			
	k = 1
	while k:
		if cam.isOpened():
			cv2.imwrite('../cache/temp.jpg',image)
			k = 0
	cam.release()
	cv2.destroyAllWindows()
