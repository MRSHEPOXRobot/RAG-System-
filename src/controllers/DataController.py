# هنا خاص بكل ال logic إلي تبع الداتا
from .BaseController import  BaseController # from file (.BaseController) import class (BaseController)
from .ProjectController import ProjectController
from fastapi import  UploadFile # import (UploadFile) to detect type of file
from models import ResponseSignal
import re #regrex ==> clean
import os

class DataController(BaseController): # DataController inherits from BaseController

    def __init__(self): # Constructor Method
        super().__init__() # Call Constructor(init) of BaseController (Base)
        self.size_scale = 1048576 # convert MB to bytes


    def validate_uploaded_file(self,file:UploadFile):
        file_extension = os.path.splitext(file.filename)[1].lower() # get the extension of the file and convert it to lower case

        if file_extension not in self.app_settings.FILE_ALLOWED_TYPES: # .pdf or .txt or .docx or .csv or .json
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        #this function takes object of the file then validate then return True/False.
        #if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES: #check type
            #return False,ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value # لازم .value علشان ده responseSignal داخل ملف enum
        if file.size > self.app_settings.FILE_MAX_SIZE*self.size_scale: #check size (max num of bytes is 10 * 1048576
            # file.size return size in bytes,so we should convert FILE_MAX_SIZE to bytes.
            return False,ResponseSignal.FILE_SIZE_EXCEEDED.value # لازم .value علشان ده responseSignal داخل ملف enum

        return True,ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, original_file_name:str, project_id:str):

        random_key = self.generate_random_string() #Random filename
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(
            orig_file_name= original_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path,random_key + "_" + cleaned_file_name


    def get_clean_file_name(self,orig_file_name:str):

        #remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]','',orig_file_name.strip() )

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ","_")

        return cleaned_file_name



