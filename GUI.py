#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import gc
import time
import faces_recognizer, faces_recognizer_haar,faces_recognizer_og


#file that contains all the read/write fonctionalities
import file_handlers
from imutils.video import VideoStream

campath = 'rtsp://admin:Admin123!!@192.168.2.50:554/Streaming/channels/101/'
#cap = cv2.VideoCapture(0)
cap = VideoStream(0).start()


APP_WIDTH = 920 #minimal width of the GUI
APP_HEIGHT = 534 #minimal height of the gui
#WIDTH  = int(cap.get(3)) #webcam's picture width
WIDTH = 605
#HEIGHT = int(cap.get(4)) #wabcam's picture height
HEIGHT = 405
#how many face-encodings to be created of each new face 
NUMBER_OF_FACES_ENCODINGS = 1 
NAME_ADDED = False
PASSWORD_ADDED = False
SHOW_PASSWORD = True
RECOGNIZE = False

#The faces are saved as pickle files, it's not actually
#a database, it's a "database"
def add_to_database(KNOWN_FACES, name):
	KNOWN_FACES[name] = faces_recognizer.KNOWN_FACES_ENCODINGS
	file_handlers.create_file(name)
	file_handlers.save_encodings(name)
	#update the current known faces dict with the freshly 
	#added faces' encodings
	KNOWN_FACES = file_handlers.load_known_faces() 
	return KNOWN_FACES

def refresh_database(name):
	KNOWN_FACES = {}
	for _ in range(NUMBER_OF_FACES_ENCODINGS):
		frame = cap.read()
		if frame is not None:
			faces_recognizer.KNOWN_FACES_ENCODINGS, NUMBER_OF_FACES_IN_FRAME = faces_recognizer.create_face_encodings(frame)
			#If there's more than one face in the frame, don't
			#consider that a valid face encoding
			if len(faces_recognizer.KNOWN_FACES_ENCODINGS) and NUMBER_OF_FACES_IN_FRAME==1:
				KNOWN_FACES = add_to_database(KNOWN_FACES, name)
				#GUI animation stuff:
				name_entry.delete(0, 'end')
				password_entry.delete(0, 'end')
				password_entry.focus()
				name_entry["state"] = "disabled"
				name_button["state"] = "disabled"
			else:
				#Show a message to the user telling them that
				#there's no valid face to encode
				messagebox.showinfo(message='Either no face, or multiple faces has been detected!\nPlease try again when problem resolved.',
									title = "Invalid name")
				name_entry.delete(0, 'end')
				name_entry.focus()
	return KNOWN_FACES

def add_new_known_face():
	faces_recognizer.KNOWN_FACES = refresh_database(name = NEW_NAME.get().lower())
	faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

def display_frames_per_second(frame, start_time):
	END_TIME = abs(start_time-time.time())
	TOP_LEFT = (0,0)
	BOTTOM_RIGHT = (116,26)
	TEXT_POSITION = (8,20)
	TEXT_SIZE = 0.5
	FONT = cv2.FONT_HERSHEY_SIMPLEX
	COLOR = (244,169,3) #BGR
	#cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0,0,0), cv2.FILLED)
	cv2.putText(frame, "FPS: {}".format(round(1/max(0.0333,END_TIME),1)), TEXT_POSITION, FONT, TEXT_SIZE,COLOR)
	return frame

#convert a fame object to an image object
def convert_to_image(frame):
	#the screen works with RGB, opencv encodes pictures in BGR
	#so to correctly display the images, color wise, we have
	#to convert them from BGR to RGB
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	frame = cv2.resize(frame, (800, 600))
	frame = cv2.flip(frame, 1)
	image = Image.fromarray(frame)
	return image

def recognize_faces (frame):
	frame = faces_recognizer_og.identify_faces(frame)
	return frame

######################
#### Main function ###
######################
frame_counter = 1
def update_frame():
	START_TIME = time.time()
	global image
	global frame_counter
	frame = cap.read()
	if frame is not None:
		frame = cv2.flip(frame, 1)
		if frame_counter%10==0:
			frame,name = recognize_faces(frame)
			textfeed.insert(1.0, name + "\n\n")
			#frame = display_frames_per_second(frame, START_TIME)
			image = convert_to_image(frame)
			frame_counter +=1
		else:
			#frame = display_frames_per_second(frame, START_TIME)
			image = convert_to_image(frame)
			frame_counter += 1
	photo.paste(image)
	root.after(round(50), update_frame) #update displayed image after: round(1000/FPS) [in milliseconds]




####################################
#### Buttons' callback functions ###
####################################


# load all the known faces in the database to the KNOWN_FACES dict
faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

# start of GUI
root = tk.Tk()
root.resizable(False, False)
# general characteristics of the GUI

##root.wm_iconbitmap(APP_ICON_PATH)
root.title("Security Cam")
root.minsize(APP_WIDTH,APP_HEIGHT)
root["bg"]="#000328"

####################
### GUI elements ###
####################


menubar = tk.Menu(root,bg='#152238')
root.config(menu=menubar)
filemenu = tk.Menu(menubar,background='#152238')
menubar.add_cascade(label='File',menu=filemenu)
filemenu.add_command(label="New", command=None)
filemenu.add_command(label="Open", command=None)
filemenu.add_command(label="Save", command=None)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)


helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=None)
helpmenu.add_command(label="About...", command=None)
menubar.add_cascade(label="Help", menu=helpmenu)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=0)
root.columnconfigure(2, weight=1)
root.rowconfigure(2, weight=1)

#nbleft = ttk.Notebook(root)
#nbcenter = ttk.Notebook(root)
#nbright = ttk.Notebook(root)

canvas = tk.Canvas(root, width=WIDTH-5, height=HEIGHT-5)
#canvas.place(relx=0.03,rely=0.052)
canvas.grid(row=0,column=1,pady=5,sticky='n')


leftframe = tk.Canvas(root,width=300,highlightthickness=1,highlightbackground='#03a9f4',bg ='#152238')
leftframe.grid(row=0,column=0,padx=5, pady=5,sticky='ns')
#leftframe.rowconfigure(0, weight=1)
#leftframe.columnconfigure(0, weight=1)

rightcanvas = tk.Canvas(root,width=400,highlightthickness=1,highlightbackground='#03a9f4',bg ='#152238')
rightcanvas.grid(row=0,column=2,padx=5, pady=5,sticky='s')
#rightcanvas.pack(side='right',fill="both", expand=True)
#rightcanvas.rowconfigure(0, weight=1)
#rightcanvas.columnconfigure(0, weight=1)

child_canvas1 = tk.Canvas(rightcanvas,height=300,width=400,highlightthickness=1,highlightbackground='#03a9f4',bg ='orange')
child_canvas1.pack()

child_canvas2 = tk.Canvas(rightcanvas,height=300,width=400,highlightthickness=1,highlightbackground='#03a9f4',bg ='#152238')
child_canvas2.pack()

textfeed = tk.Text(child_canvas1,width=50,bg = "#152238",
                             fg = "#03a9f4",
                             font = "Calibri 11",
                             padx = 5,
                             pady = 5)
textfeed.pack()




### Initial frame ###

frame = cap.read()
frame = cv2.resize(frame, (600, 400))
if frame is not None:
	image = convert_to_image(frame)
	photo = ImageTk.PhotoImage(image=image)
	canvas.create_image(WIDTH, HEIGHT, image=photo, anchor="se")

### Start the show ###


if __name__ == '__main__':
	update_frame()

#create the GUI.
root.mainloop()

#free memory
cap.stop()
gc.collect()
