import face_recognition
import os
from os import listdir
from os.path import isfile, join
import numpy
import time
import random
import cv2
from gtts import gTTS

# Computer voice
def speak_out(text):
    tts = gTTS(text, lang='en')
    tts.save("/Users/zhangpeng/tensorflow/FR/tts.mp3")
    os.system("afplay /Users/zhangpeng/tensorflow/FR/tts.mp3")


# Import known faces if any

known_face_encodings = []
known_face_names = []

path="/Users/zhangpeng/tensorflow/FR/known_faces"
face_images = [ f for f in listdir(path) if isfile(join(path,f)) ]

for face_image in face_images:
    face_encoding=face_recognition.face_encodings(face_recognition.load_image_file("%s/%s" %(path,face_image)))[0]
    face_name=face_image.split(".")[0]
    known_face_encodings.append(face_encoding)
    known_face_names.append(face_name)                                         
                                                  
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

welcome=["Have a good day","Wish you a happy day","You look so smart","I know you"]

ask_name_input=["please input your name","type your name, please","I want to know your name. Please type it"
          ,"please tell me your name by the keyboard"]

last_face_names=[]
last_k_face_names=[]

video_capture = cv2.VideoCapture(0) 
cv2.namedWindow('Video',cv2.WINDOW_NORMAL)
cv2.resizeWindow('Video', 800,600)
                     
    
# Start main progress    
count=0
while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    #print(frame.shape)
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding,tolerance=0.43)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

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
        cv2.rectangle(frame, (left, bottom), (right, bottom+35), (0, 0, 255), cv2.FILLED)
                
        font = cv2.FONT_HERSHEY_DUPLEX
       
        cv2.putText(frame, name, (left + 6, bottom + 25), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)
    keyboard_input=cv2.waitKey(1)
    if keyboard_input & 0xFF == ord('q'):
        break  
        
    if(face_names!=[]):
        
        if(face_names==last_face_names and "Unknown" in face_names):
            count=count+1
        else:
            count=0
     
        k_face_names=[]

        for face in face_names:
            if(face!="Unknown"):
                k_face_names.append(face)
            
        if(k_face_names!=last_k_face_names and k_face_names!=[]):
            name_list=""
            for name in k_face_names:
                if name not in name_list:
                    name_list=name_list+name+", "
            speak_out(name_list+welcome[random.randint(0,len(welcome)-1)])
            last_k_face_names=k_face_names
        
        last_face_names=face_names
  
        #Handle unknow faces; ask for name input 
        if(count==20):
            (ntop,nright,nbottom,nleft)=face_locations[face_names.index("Unknown")]            
            ntop *= 4
            nright *= 4
            nbottom *= 4
            nleft *= 4
            nface_image=frame[ntop:nbottom,nleft:nright]
        

            frame[:,:nleft,:]=frame[:,:nleft,:]*0.3
            frame[:,nright:,:]=frame[:,nright:,:]*0.3
            frame[:ntop,nleft:nright:,:]=frame[:ntop,nleft:nright:,:]*0.3
            frame[nbottom:,nleft:nright:,:]=frame[nbottom:,nleft:nright:,:]*0.3

    
            cv2.rectangle(frame, (nleft, ntop), (nright, nbottom), (255, 0, 0), 4)
                        
            
            key_inputs=[]
            cv2.imshow('Video', frame)
            key_input=cv2.waitKey(1)
            speak_out("Hi, new friend!"+ask_name_input[random.randint(0,len(ask_name_input)-1)])


            wait_count=0
            while((key_input & 0xFF)!=13 and wait_count<6000):
                key_inputs.append(key_input)
                key_input=cv2.waitKey(1)
                if(key_input!=-1):
                    wait_count=0
                else:
                    wait_count += 1
                
            if(wait_count==6000):
                speak_out("You did not input anything")
            else:
                key_inputs=list(filter((-1).__ne__, key_inputs))
                while 8 in key_inputs:
                    bs_position=key_inputs.index(8)
                    if(bs_position>0):
                        del key_inputs[bs_position-1]
                        del key_inputs[bs_position-1]
                    else:
                        del dey_inputs[bs_position]
                    
            
                key_chars=''.join(chr(i) for i in key_inputs)

                name=str(key_chars)
                speak_out("Thank you")
            
                cv2.imwrite('%s/%s.png' % (path, name),nface_image)
                known_face_encodings.append(face_encodings[face_names.index("Unknown")])
                known_face_names.append(name)
            
            count=0
        
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()



