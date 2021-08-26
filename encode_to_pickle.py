import face_recognition
import pickle
import os

# Load a sample picture and learn how to recognize it.
alphanso_image = face_recognition.load_image_file("alphanso.jpg")
alphanso_face_encoding = face_recognition.face_encodings(alphanso_image)[0]

# Load a second sample picture and learn how to recognize it.
piper_image = face_recognition.load_image_file("piper.jpg")
piper_face_encoding = face_recognition.face_encodings(piper_image)[0]

# Load a second sample picture and learn how to recognize it.
ronald_image = face_recognition.load_image_file("ronald.jpg")
ronald_face_encoding = face_recognition.face_encodings(ronald_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    alphanso_face_encoding,
    piper_face_encoding,
    ronald_face_encoding
]
known_face_names = [
    "Alphonso Murray",
    "Brictoni Piper",
    "Ronald Brown"
]

# dump the facial encodings + names to disk
print("[INFO] serializing {} encodings...")
data = {"embeddings": known_face_encodings, "names": known_face_names}
f = open(os.getcwd()+'/embeddings.pickle', "wb")
f.write(pickle.dumps(data))
f.close()