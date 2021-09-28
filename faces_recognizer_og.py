import cv2
import face_recognition
import pickle
import numpy as np
import timeit



# load the face embeddings
print("[INFO] loading face encodings...")
known_data = pickle.loads(open('C:/Users/Piper/Downloads/Face-Recognition-GUI-Python-master/Face-Recognition-GUI-Python-master/embeddings2.pickle',"rb").read())


def identify_faces(frame):


    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Check processing time start
    tic = timeit.default_timer()

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame,3)
    # Check processing time for encoding
    toc = timeit.default_timer()
    print(toc - tic)

    if face_locations:
        print('face detected')

        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


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
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

            # Draw a label with a name below the face
            #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0))
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.8, (255, 0, 0), 1)

            locations = (top,right,bottom,left)

            return frame,name,locations
    else:
        print('No face detected')
        return frame,'None',None

