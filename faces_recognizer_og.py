import cv2
from datetime import datetime
import face_recognition
import pickle
import numpy as np
import timeit
import os
import time
from PIL import Image

# Crop Padding
left = 10
right = 10
top = 10
bottom = 10
grab = True


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


# load the face embeddings
print("[INFO] loading face embeddings...")
known_data = pickle.loads(open('C:/Users/Piper/Downloads/Face-Recognition-GUI-Python-master/Face-Recognition-GUI-Python-master/embeddings.pickle',"rb").read())


def identify_faces(frame):
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    # Check processing time start
    tic = timeit.default_timer()

    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Check processing time for encoding
    toc = timeit.default_timer()
    print(toc - tic)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_data["embeddings"], face_encoding)
        name = "Unknown"

        # # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_data["embeddings"], face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_data["names"][best_match_index]
            # print(name)

        face_names.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        #now = datetime.now()  # current date and time
        #date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        #stamp = name + date_time

        return frame, name

    stamp = 'test'


#check if face has recently been displayed in recent activity feed
def check_recent(name,timestamp,frame):
    recent_activity_dict = {}
    if name not in recent_activity_dict:
        headshot = crop_face(frame)
        recent_activity_dict[name]=timestamp
        return headshot
    else:
        if time.time() - recent_activity_dict[name] > 60:
           headshot = crop_face(frame)
           recent_activity_dict[name] = time.time()
           return headshot
        else:
            return None


def crop_face(frame):
    None