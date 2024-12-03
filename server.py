from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import face_recognition

app = FastAPI()

BASE_DIR = "images"
os.makedirs(BASE_DIR, exist_ok=True)

@app.post("/save-images/")
async def save_images(face_image: UploadFile = File(...), data_image: UploadFile = File(...)):
    temp_face_path = os.path.join(BASE_DIR, "temp_face.jpg")
    
    try:
        with open(temp_face_path, "wb") as buffer:
            shutil.copyfileobj(face_image.file, buffer)
        
        temp_data_path = os.path.join(BASE_DIR, "temp_data.jpg")
        with open(temp_data_path, "wb") as buffer:
            shutil.copyfileobj(data_image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving the images: {str(e)}")

    try:
        uploaded_face = face_recognition.load_image_file(temp_face_path)
        uploaded_encoding = face_recognition.face_encodings(uploaded_face)[0]
    except IndexError:
        os.remove(temp_face_path)
        raise HTTPException(status_code=400, detail="No face found in the uploaded image.")
    
    
    for dir_name in os.listdir(BASE_DIR):
        dir_path = os.path.join(BASE_DIR, dir_name)  
        if dir_name.startswith('_') and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)  
        

    for dir_name in os.listdir(BASE_DIR):
        if not dir_name.startswith('_'):
            dir_path = os.path.join(BASE_DIR, dir_name)
            face_path = os.path.join(dir_path, "face.jpg")
            data_path = os.path.join(dir_path, "data.jpg")

            if os.path.exists(face_path):
                try:
                    saved_face = face_recognition.load_image_file(face_path)
                    saved_encoding = face_recognition.face_encodings(saved_face)[0]
                    matches = face_recognition.compare_faces([saved_encoding], uploaded_encoding)
                    if matches[0]:
                        with open(face_path, "wb") as buffer:
                            shutil.copyfileobj(face_image.file, buffer)
                        with open(data_path, "wb") as buffer:
                            shutil.copyfileobj(data_image.file, buffer)
                        os.remove(temp_face_path)
                        os.remove(temp_data_path)
                        return {"message": "User already exists. Images replaced.", "directory_id": dir_name}
                except IndexError:
                    continue

    dir_id = str(uuid.uuid4())
    new_dir = os.path.join(BASE_DIR, dir_id)
    os.makedirs(new_dir, exist_ok=True)
    final_data_path = os.path.join(new_dir, "data.jpg")
    final_image_path = os.path.join(new_dir, "face.jpg")

    shutil.copy(temp_data_path, final_data_path)
    shutil.copy(temp_face_path, final_image_path)

    os.remove(temp_face_path)
    os.remove(temp_data_path)
    
    return {"message": "New user. Images saved successfully.", "directory_id": dir_id}



@app.get("/get-data-image/")
async def get_data_image(face_image: UploadFile = File(...)):
    temp_face_path = os.path.join(BASE_DIR, "temp_face.jpg")
    with open(temp_face_path, "wb") as buffer:
        shutil.copyfileobj(face_image.file, buffer)

    try:
        uploaded_face = face_recognition.load_image_file(temp_face_path)
        uploaded_encoding = face_recognition.face_encodings(uploaded_face)[0]
    except IndexError:
        os.remove(temp_face_path)
        raise HTTPException(status_code=400, detail="No face found in the uploaded image.")

    for dir_name in os.listdir(BASE_DIR):
        dir_path = os.path.join(BASE_DIR, dir_name)
        if dir_name.startswith("_"):
            continue

        face_path = os.path.join(dir_path, "face.jpg")
        data_path = os.path.join(dir_path, "data.jpg")

        if os.path.exists(face_path) and os.path.exists(data_path):
            try:
                saved_face = face_recognition.load_image_file(face_path)
                saved_encoding = face_recognition.face_encodings(saved_face)[0]
                matches = face_recognition.compare_faces([saved_encoding], uploaded_encoding)
                if matches[0]:
                    renamed_dir_path = os.path.join(BASE_DIR, f"_{dir_name}")
                    os.rename(dir_path, renamed_dir_path)

                    response = FileResponse(renamed_dir_path + '/data.jpg')
                    return response
            except IndexError:
                continue

    os.remove(temp_face_path)
    raise HTTPException(status_code=404, detail="No matching face found.")

