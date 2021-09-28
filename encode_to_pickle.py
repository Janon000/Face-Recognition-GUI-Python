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

# Load a second sample picture and learn how to recognize it.
davia_image = face_recognition.load_image_file("Davia.jpg")
davia_face_encoding = face_recognition.face_encodings(davia_image)[0]

# Load a second sample picture and learn how to recognize it.
trudy_image = face_recognition.load_image_file("Trudy.jpg")
trudy_face_encoding = face_recognition.face_encodings(davia_image)[0]

# Load a second sample picture and learn how to recognize it.
asheika_image = face_recognition.load_image_file("Asheika.jpg")
asheika_face_encoding = face_recognition.face_encodings(davia_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    alphanso_face_encoding,
    piper_face_encoding,
    ronald_face_encoding,
    davia_face_encoding,
    trudy_face_encoding,
    asheika_face_encoding
]
known_face_names = [
    "Alphonso Murray",
    "Brictoni Piper",
    "Ronald Brown",
    "Davia Clarke",
    "Trudy-Ann Brooks",
    "Asheika Vassel"
]

# dump the facial encodings + names to disk
print("[INFO] serializing {} encodings...")
data = {"embeddings": known_face_encodings, "names": known_face_names}
f = open(os.getcwd()+'/embeddings2.pickle', "wb")
f.write(pickle.dumps(data))
f.close()