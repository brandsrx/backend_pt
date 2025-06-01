import os
import uuid
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
import multiprocessing
from io import BytesIO
from flask import url_for

class UploadFile:
    def __init__(self, username: str, target_folder: str):
        if not target_folder:
            raise ValueError("Debes proporcionar una carpeta de destino.")

        self.username = username
        self.target_folder = target_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg'}
        self.max_workers = multiprocessing.cpu_count() * 2
        self.static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        self.base_folder = os.path.join(self.static_folder, 'uploads', self.username, self.target_folder)
        os.makedirs(self.base_folder, exist_ok=True)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def compress_file(self, file, save_path, max_size=1024, quality=85):
        try:
            img = Image.open(file)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail((max_size, max_size))
            root, _ = os.path.splitext(save_path)
            save_path_jpg = root + ".jpg"
            img.save(save_path_jpg, format='JPEG', quality=quality, optimize=True)
            return True
        except Exception as e:
            print(f"Error procesando imagen {file.filename}: {e}")
            return False
        finally:
            if 'img' in locals():
                img.close()

    def process_image(self,file):
        url:str = ""
        filename = f"{uuid.uuid4()}.jpg"
        save_path = os.path.join(self.base_folder,filename)
        in_memory_file = BytesIO(file.read())
        in_memory_file.seek(0)
        in_memory_file.name = file.filename
        if self.compress_file(in_memory_file,save_path):
            return f"uploads/{self.username}/{self.target_folder}/{filename}"
        return None
    
    def process_images(self, files):
        saved_urls = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            name_url = []
            for file in files:
                if not self.allowed_file(file.filename):
                    continue

                filename = f"{uuid.uuid4()}.jpg"
                save_path = os.path.join(self.base_folder, filename)
                in_memory_file = BytesIO(file.read())
                in_memory_file.seek(0)
                in_memory_file.name = file.filename  # Para errores más claros
                name_url.append(filename)
                futures.append(executor.submit(self.compress_file, in_memory_file, save_path))

            for index,future in enumerate(futures):
                result = future.result()
                if result:
                    saved_urls.append(f"uploads/{self.username}/{self.target_folder}/{name_url[index]}")

        return saved_urls
