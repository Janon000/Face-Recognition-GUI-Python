"""
Manually encode images to pickle file if needed
"""

import face_recognition
import pickle
import os

# Load a sample picture and learn how to recognize it.
sample_image = face_recognition.load_image_file("sample.jpg")
sample_face_encoding = face_recognition.face_encodings(sample_image)[0]


# Create arrays of known face encodings and their names
known_face_encodings = [
    sample_face_encoding,
]
known_face_names = [
    "John Doe",
]

# dump the facial encodings + names to disk
print("[INFO] serializing {} encodings...")
data = {"embeddings": known_face_encodings, "names": known_face_names}
f = open(os.getcwd()+'/embeddings.pickle', "wb")
f.write(pickle.dumps(data))
f.close()
