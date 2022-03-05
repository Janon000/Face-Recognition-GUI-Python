"""
Simple Gui interface
"""
import math
import os
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageTk
import cv2
import time
import face_recognizer_threaded
import sql_handler as sql
import uuid
import csv
from threading import Thread, Lock
import queue

# Directory recognized faces in feed
image_directory = os.getcwd() + '/feed_faces/'
# Directory where new faces are stored
snapshot_directory = os.getcwd() + '/snapshot_faces'
match_directory = os.getcwd() + '/match_directory'

# Path webcam or rtsp camera
campath = 0


APP_WIDTH = 920  # minimal width of the GUI
APP_HEIGHT = 534  # minimal height of the gui
# WIDTH  = int(cap.get(3)) #webcam's picture width
WIDTH = 605
# HEIGHT = int(cap.get(4)) #wabcam's picture height
HEIGHT = 405
canvas_height = 300
canvas_width = 400


# convert a frame object to an image object
def convert_to_image(frame):
    # the screen works with RGB, opencv encodes pictures in BGR
    # so to correctly display the images, color wise, we have
    # to convert them from BGR to RGB
    # img_gray = cv2.cvtColor(np.float32(frame), cv2.COLOR_BGR2GRAY)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (1280, 720))
    # frame = cv2.flip(frame, 1)
    # image = cv2.imread(frame)
    image = Image.fromarray(frame)
    return image


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
    pil_image = Image.fromarray(frame[(max(top - v_padding, 0)):(max(bottom + v_padding, 400)),
                                (max(left - h_padding, 0)):(max(right + h_padding, 300))])

    # save to dictionary to avoid garbage collection
    head_images[name] = ImageTk.PhotoImage(pil_image)

    # store image to file system
    filename = store_image(pil_image)
    return head_images[name], filename


def store_image(pil_image):
    # store image to filesystem and filepath to mysql
    filename = image_directory + str(uuid.uuid4().hex + '.jpg')
    pil_image.save(filename)
    return filename


def store_snapshot(pil_image):
    # store image to filesystem and filepath to mysql
    filename = snapshot_directory + str(uuid.uuid4().hex + '.jpg')
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
        fieldnames = ['date', 'name', 'imagepath']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # writer.writeheader()
        writer.writerow({'date': date_time, 'name': name, 'imagepath': filename})


class Threaded_Camera:
    def __init__(self):
        self.active = True
        self.cap = cv2.VideoCapture(campath)  # campath
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        # default value at start
        self.results = []
        self.frame = None
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.mutex = Lock()

        # Start frame retrieval thread
        self.q = queue.Queue()
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    # One of three options for displaying frames.
    def show_frame(self):
        print("Started")
        while self.cap.isOpened():
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

            self.frame = frame
            self.results = results

    # Loading frames using mutex method
    def show_frame_mutex(self):
        print("Started")
        while self.cap.isOpened():
            self.mutex.acquire()
            (status, frame_raw) = self.cap.grab()
            self.mutex.release()
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

            self.frame = frame
            self.results = results

    # Load frames using queueing
    def show_frame_queue(self):
        print("Started")
        while self.cap.isOpened():
            (status, frame_raw) = self.cap.read()
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass

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

            self.q.put(frame, results)
            self.frame = frame
            self.results = results

    def is_active(self):
        return self.active

    def do_recognition(self):
        if not hasattr(self, 'frame'):
            return
        self.results = recognize_faces(self.frame)
        print(self.results)

    def get_frame_results(self):
        return self.frame, self.results

    def get_frame_queue(self):
        return self.q.get()

    def get_frame_mutex(self):
        self.mutex.acquire()
        (status, frame_raw) = self.cap.retrieve()
        self.mutex.release()
        return self.frame, self.results


class Tkinter_gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.threaded_camera = Threaded_Camera()

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

        self.camera_canvas = tk.Canvas(self, width=800 - 5, height=600 - 5)
        self.camera_canvas.grid(row=0, column=1, pady=5, sticky='n')

        # self.leftcanvas = tk.Canvas(self, width=300, highlightthickness=1,\
        # highlightbackground='#03a9f4', bg='#152238')
        # self.leftcanvas.grid(row=0, column=0, padx=5, pady=5, sticky='ns')

        self.rightcanvas = tk.Canvas(self, width=400, highlightthickness=1, highlightbackground='#03a9f4', bg='#152238')
        self.rightcanvas.grid(row=0, column=2, padx=5, pady=5, sticky='s')

        self.style = ttk.Style()
        self.style.theme_create(
            "name", parent="alt", settings={
                ".": {"configure": {"background": '#152238',
                                    "foreground": "white",
                                    "relief": "flat"}},
                "TLabel": {"configure": {"foreground": "white",
                                         "padding": 10,
                                         "font": ("Calibri", 16)}},
                "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}
                              },
                "TNotebook.Tab": {
                    "configure": {"relief": "flat",
                                  "bordercolor": '#03a9f4',
                                  "darkcolor": '#152238',
                                  "lightcolor": '#152238',
                                  "padding": [5, 1], "background": '#152238'
                                  },
                    "map": {"background": [("selected", '#152238')],
                            "expand": [("selected", [1, 1, 1, 0])]}
                }
            })

        self.style.theme_use("name")

        # create a notebook
        self.notebook = ttk.Notebook(self.rightcanvas)
        self.notebook.pack(expand=True)

        # Frame which contains canvas'
        self.rightframe = tk.Frame(self.notebook, highlightbackground='#03a9f4', width=400)
        self.rightframe.pack(expand=True)

        # testframe
        # self.rightframe2 = tk.Frame(self.notebook, bg ='red')
        # self.rightframe2.pack(expand=True)

        # canvas for textfeed
        self.textfeed_canvas = tk.Canvas(self.rightframe, height=200, width=400, highlightthickness=1,
                                         highlightbackground='#03a9f4',
                                         bg='#03a9f4')
        self.textfeed_canvas.pack()

        # canvas for headshots of recently captured faces
        self.headshot_canvas = tk.Canvas(self.rightframe, height=300, width=400, highlightthickness=1,
                                         highlightbackground='#03a9f4',
                                         bg='#152238')
        self.headshot_canvas.pack()

        # Text widget inside textfeed canvas
        self.textfeed = tk.Text(self.textfeed_canvas, width=55, bg="#152238", bd=0, state='disabled',
                                fg="#03a9f4",
                                font="calibri 11",
                                padx=5,
                                pady=5,
                                highlightthickness=0)
        self.textfeed.pack(expand=True, fill='both')

        # add canvas to notebook
        self.notebook.add(self.rightframe, text='Recent Activity')
        # self.notebook.add(self.rightframe2, text='test')

        # buttom to allow face recognition
        self.recognition_button = tk.Button(self, text="Recognize", command=self.enable_recognition,
                                            bg="#152238", fg="white", activebackground='white')
        self.recognition_button.grid(row=0, column=1, pady=5, sticky='s')
        self.recognition_button.bind(self.enable_recognition)
        self.recognition_button.focus()

        # button to take picture
        self.snapshot_button = tk.Button(self, text="Snapshot", command=self.take_snapshot,
                                         bg="#152238", fg="white", activebackground='white')
        self.snapshot_button.grid(row=0, column=1, pady=50, sticky='s')
        self.snapshot_button.bind(self.take_snapshot)
        self.snapshot_button.focus()

        # buttom to update pickle
        self.update_button = tk.Button(self, text="Update", command=self.update_pickle,
                                       bg="#152238", fg="white", activebackground='white')
        self.update_button.grid(row=0, column=1, pady=100, sticky='s')
        self.update_button.bind(self.update_pickle)
        self.update_button.focus()

        self.running = True
        self.RECOGNIZE = False
        self.update_frame()

    def start(self):
        if not self.running:
            self.running = True
            self.update_frame()

    def stop(self):
        if self.running:
            self.running = False

    def enable_recognition(self):

        if self.RECOGNIZE:
            self.RECOGNIZE = False
            self.recognition_button["bg"] = "#152238"
        else:
            self.RECOGNIZE = True
            self.recognition_button["bg"] = "red"
            print("recognizing..")

    def take_snapshot(self):
        frame = self.threaded_camera.frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame)
        # store image to file system
        filename = store_image(pil_image)
        print(filename)

    def update_pickle(self):
        self.snap_path = filedialog.askopenfile(mode='r', initialdir=os.getcwd(), title='Select an image',
                                                filetypes=[("jpg files", "*.jpg")])
        if self.snap_path:
            self.new_name = simpledialog.askstring('Update Database', 'Enter Name', parent=self.camera_canvas)
            self.warn_message = face_recognizer_threaded.enc(self.snap_path.name, self.new_name)
            if self.warn_message is not None:
                tkinter.messagebox.showwarning(title='Error', message=self.warn_message)

    # Update gui with frames from camera thread
    def update_frame(self):

        if self.RECOGNIZE:
            self.threaded_camera.do_recognition()
        else:
            self.threaded_camera.results = None

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
                        self.headshot_canvas.create_image(canvas_width, canvas_height, image=head_images[name],
                                                          anchor="se")
                        # save to csv instead of db
                        save_to_csv(date_time, name, filename)

            self.image = convert_to_image(frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.camera_canvas.create_image(1280, 720, image=self.photo, anchor="se")
        elif frame is not None:
            self.image = convert_to_image(frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.camera_canvas.create_image(1280, 720, image=self.photo, anchor="se")
        self.after(round(40), self.update_frame)


if __name__ == '__main__':
    Gui = Tkinter_gui()
    Gui.mainloop()

    # print('blocking')
# while Gui.threaded_camera.is_active():
#  Gui.threaded_camera.do_recognition()
# Gui.update_frame()
