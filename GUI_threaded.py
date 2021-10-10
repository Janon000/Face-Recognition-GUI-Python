import math
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import time
import face_recognizer_threaded
import imutils
import sql_handler as sql
import uuid
import mysql.connector
import csv
from threading import Thread
import numpy as np
import queue

# file that contains all the read/write fonctionalities
import file_handlers
from imutils.video import VideoStream

image_directory = os.getcwd()+'/feed_faces/'
match_directory = os.getcwd()+'/match_directory'
unknown_directory = os.getcwd()+'/unknown_directory'

campath = 'rtsp://admin:Admin123!!@192.168.2.50:554/Streaming/channels/101/'
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

#cap = VideoStream(0).start()

APP_WIDTH = 920  # minimal width of the GUI
APP_HEIGHT = 534  # minimal height of the gui
# WIDTH  = int(cap.get(3)) #webcam's picture width
WIDTH = 605
# HEIGHT = int(cap.get(4)) #wabcam's picture height
HEIGHT = 405
canvas_height = 300
canvas_width = 400
# how many face-encodings to be created of each new face
NUMBER_OF_FACES_ENCODINGS = 1
NAME_ADDED = False
PASSWORD_ADDED = False
SHOW_PASSWORD = True
RECOGNIZE = False


# The faces are saved as pickle files, it's not actually
# a database, it's a "database"
def add_to_database(KNOWN_FACES, name):
    KNOWN_FACES[name] = faces_recognizer.KNOWN_FACES_ENCODINGS
    file_handlers.create_file(name)
    file_handlers.save_encodings(name)
    # update the current known faces dict with the freshly
    # added faces' encodings
    KNOWN_FACES = file_handlers.load_known_faces()
    return KNOWN_FACES


def refresh_database(name):
    KNOWN_FACES = {}
    for _ in range(NUMBER_OF_FACES_ENCODINGS):
        frame = cap.read()
        if frame is not None:
            faces_recognizer.KNOWN_FACES_ENCODINGS, NUMBER_OF_FACES_IN_FRAME = faces_recognizer.create_face_encodings(
                frame)
            # If there's more than one face in the frame, don't
            # consider that a valid face encoding
            if len(faces_recognizer.KNOWN_FACES_ENCODINGS) and NUMBER_OF_FACES_IN_FRAME == 1:
                KNOWN_FACES = add_to_database(KNOWN_FACES, name)
                # GUI animation stuff:
                name_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                password_entry.focus()
                name_entry["state"] = "disabled"
                name_button["state"] = "disabled"
            else:
                # Show a message to the user telling them that
                # there's no valid face to encode
                messagebox.showinfo(
                    message='Either no face, or multiple faces has been detected!\nPlease try again when problem resolved.',
                    title="Invalid name")
                name_entry.delete(0, 'end')
                name_entry.focus()
    return KNOWN_FACES


def add_new_known_face():
    faces_recognizer.KNOWN_FACES = refresh_database(name=NEW_NAME.get().lower())
    faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()


def display_frames_per_second(frame, start_time):
    END_TIME = abs(start_time - time.time())
    TOP_LEFT = (0, 0)
    BOTTOM_RIGHT = (116, 26)
    TEXT_POSITION = (8, 20)
    TEXT_SIZE = 0.5
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    COLOR = (244, 169, 3)  # BGR
    # cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0,0,0), cv2.FILLED)
    cv2.putText(frame, "FPS: {}".format(round(1 / max(0.0333, END_TIME), 1)), TEXT_POSITION, FONT, TEXT_SIZE, COLOR)
    return frame


# convert a fame object to an image object
def convert_to_image(frame):
    # the screen works with RGB, opencv encodes pictures in BGR
    # so to correctly display the images, color wise, we have
    # to convert them from BGR to RGB
    #img_gray = cv2.cvtColor(np.float32(frame), cv2.COLOR_BGR2GRAY)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (1280, 720))
    # frame = cv2.flip(frame, 1)
    #image = cv2.imread(frame)
    image = Image.fromarray(frame)
    return image


def enable_recognition():
    global RECOGNIZE
    if RECOGNIZE:
        RECOGNIZE = False
        recognition_button["bg"] = "#152238"
    else:
        RECOGNIZE = True
        recognition_button["bg"] = "red"
        print("recognizing..")


def recognize_faces(frame):
    frame = face_recognizer_threaded.identify_faces(frame)
    return frame


# initialize objects needed for face image cropping and saving to database/file system
head_images = {}
recent_activity_dict = {}
db_connection = sql.create_db_connection1()


# check if face has been displayed in recent activity canvas within the last 10 seconds,
# if not crop the face out of the frame and return the image to canvas
def check_recent(frame, name, locations):
    if name in recent_activity_dict and time.time() - recent_activity_dict[name] <= 10:
        return None, None
    else:
        recent_activity_dict[name] = time.time()
        headshot, filename = crop_face(frame, name, locations)
        return headshot, filename


# crop the detected face to the dimensions of the canvas
def crop_face(frame, name, locations):
    top, right, bottom, left = locations
    # determine vertical and horizontal padding needed for the detected face
    v_padding = math.floor((canvas_height - (bottom - top)) / 2)
    h_padding = math.floor((canvas_width - (right - left)) / 2)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame[(max(top - v_padding,0)):(max(bottom + v_padding,400)), (max(left - h_padding,0)):(max(right + h_padding,300))])

    # save to dictionary to avoid garbage collection
    head_images[name] = ImageTk.PhotoImage(pil_image)

   #store image to file system
    filename = store_image(pil_image)
    return head_images[name], filename


def store_image(pil_image):
    # store image to filesystem and filepath to mysql
    filename = image_directory + str(uuid.uuid4().hex + '.jpg')
    pil_image.save(filename)
    return filename


def save_to_sql(connection, date_time, name, filename):
    # save to sql database
    mycursor = connection.cursor()
    headshot_sql = "INSERT INTO detected3 VALUES (%s, %s, %s)"
    val = (date_time, name, filename)
    mycursor.execute(headshot_sql, val)
    connection.commit()

def save_to_csv(date_time, name, filename):
    with open('outfile.csv', 'a', newline='') as f:
        fieldnames = ['date', 'name','imagepath']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        #writer.writeheader()
        writer.writerow({'date': date_time, 'name': name, 'imagepath':filename})


class Threaded_Camera:
    def __init__(self):
        self.active = True
        self.cap = cv2.VideoCapture(0)

        # default value at start
        self.results = []
        self.frame = None

        # Start frame retrieval thread
        self.thread_queue = queue.Queue()
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

        # Start results thread
        #self.results_thread = Thread(target=self.do_recognition())
        #self.results_thread.daemon = True
        #self.results_thread.start()

    def show_frame(self):
        print("Started")
        while self.cap.isOpened():
            #(frame_raw) = self.cap.read()
            (status, frame_raw) = self.cap.read()
            frame = cv2.flip(frame_raw, 1)
            results = []
            if status:
                if self.results:
                    results = self.results
                    for result in results:
                        name = result.get('name')
                        top = result.get('top')
                        right = result.get('right')
                        left = result.get('left')
                        bottom = result.get('bottom')

                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

                        # Draw a label with a name below the face
                        # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0))
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 0, 0), 1)

            #cv2.imshow('test',frame)


            self.frame = frame
            self.results = results
            #self.thread_queue.put(frame)


    def is_active(self):
        return self.active

    def do_recognition(self):
        if not hasattr(self, 'frame'):
            return
        self.results = recognize_faces(self.frame)

    def get_frame_results(self):
        return self.frame, self.results


class Tkinter_gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.threaded_camera = Threaded_Camera()
        #self.threaded_camera.do_recognition()

        # initialize objects needed for face image cropping and saving to database/file system
        self.head_images = {}
        self.recent_activity_dict = {}

        self.resizable(False, False)
        # general characteristics of the GUI
        self.title("Security Cam")
        self.minsize(APP_WIDTH, APP_HEIGHT)
        self["bg"] = "#000328"

        self.menubar = tk.Menu(self, bg='#152238')
        self.config(menu=self.menubar)
        self.filemenu = tk.Menu(self.menubar, background='#152238')
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label="New", command=None)
        self.filemenu.add_command(label="Open", command=None)
        self.filemenu.add_command(label="Save", command=None)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Help Index", command=None)
        self.helpmenu.add_command(label="About...", command=None)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

        self.camera_canvas = tk.Canvas(self, width=1280 - 5, height=720 - 5)
        self.camera_canvas.grid(row=0, column=0, pady=5, sticky='n')

        # leftframe = tk.Canvas(root, width=300, highlightthickness=1, highlightbackground='#03a9f4', bg='#152238')
        # leftframe.grid(row=0, column=0, padx=5, pady=5, sticky='ns')

        self.rightcanvas = tk.Canvas(self, width=400, highlightthickness=1, highlightbackground='#03a9f4', bg='#152238')
        self.rightcanvas.grid(row=0, column=1, padx=5, pady=5, sticky='s')

        self.textfeed_canvas = tk.Canvas(self.rightcanvas, height=200, width=200, highlightthickness=1,
                                    highlightbackground='#03a9f4',
                                    bg='orange')
        self.textfeed_canvas.pack()

        self.headshot_canvas = tk.Canvas(self.rightcanvas, height=300, width=400, highlightthickness=1,
                                    highlightbackground='#03a9f4',
                                    bg='#152238')
        self.headshot_canvas.pack()

        self.textfeed = tk.Text(self.textfeed_canvas, width=50, bg="#152238", bd=1, state='disabled',
                           fg="#03a9f4",
                           font="Calibri 11",
                           padx=5,
                           pady=5)
        self.textfeed.pack()

        self.recognition_button = tk.Button(self, text="Recognize", command=enable_recognition,
                                       bg="#152238", fg="white", activebackground='white')
        self.recognition_button.grid(row=0, column=0, pady=5, sticky='n')
        self.recognition_button.bind(enable_recognition)
        self.recognition_button.focus()

        self.running = True
        self.update_frame()




    def start(self):
        if not self.running:
            self.running = True
            self.update_frame()

    def stop(self):
        if self.running:
            self.running = False

    #Update gui with frames from camera thread
    def update_frame(self):
        self.threaded_camera.do_recognition()

        print('updating')

        # Get a frame from the video source
        frame, results = self.threaded_camera.get_frame_results()

        if frame is not None and results is not None:
            for result in results:
                name = result.get('name')
                top = result.get('top')
                right = result.get('right')
                left = result.get('left')
                bottom = result.get('bottom')
                locations = (top, right, bottom, left)
                if locations:
                    headshot, filename = check_recent(frame, name, locations)
                    if headshot is not None:
                        # insert name and timestamp into text widget
                        date_time = time.strftime('%Y-%m-%d, %H:%M:%S')
                        self.textfeed.configure(state='normal')
                        self.textfeed.insert(1.0, f"{name} {date_time} " + "\n\n")
                        self.textfeed.configure(state='disabled')
                        self.headshot_canvas.delete()
                        # update canvas with image of identified person
                        self.headshot_canvas.create_image(canvas_width, canvas_height, image=head_images[name], anchor="se")
                        #save to csv instead of db
                        save_to_csv(date_time, name, filename)

            self.image = convert_to_image(frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.camera_canvas.create_image(1280, 720, image=self.photo, anchor="se")
        self.after(round(40), self.update_frame)


if __name__ == '__main__':

    Gui = Tkinter_gui()
    Gui.mainloop()

    #print('blocking')
   # while Gui.threaded_camera.is_active():
      #  Gui.threaded_camera.do_recognition()
       # Gui.update_frame()