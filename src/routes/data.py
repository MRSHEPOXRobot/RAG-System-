from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request,File
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
import aiofiles #library used to deal with files chunk by chunk (async)
from models import ResponseSignal
import logging
from routes.schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data", #Any endpoint will start with this prefix
    tags=  ["api_v1","data"], #2 tags
) # define object

@data_router.post("/upload/{project_id}") # endpoint called upload to upload the file and the project_id is a path parameter
async def upload_data(request: Request,project_id : str, file : UploadFile = File(...), #Function of endpoint its type is string,because we don't make any math operations.
                      #parameter file is a type of UploadFile.
                      app_settings : Settings = Depends(get_settings ) ): # app_setting is a variable of type settings and depends on get_settings

    #project_model used to deal with the project collection in the database
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    data_controller = DataController()
    # 2:validate the file properties لازم أختبر الملف إلي جايلي
    print("================================")
    print("FILE NAME:", file.filename)
    print("CONTENT TYPE:", file.content_type)
    print("FILE SIZE:", file.size)
    print("ALLOWED TYPES:", app_settings.FILE_ALLOWED_TYPES)
    print("================================")

    is_valid,result_signal = data_controller.validate_uploaded_file(file = file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            # ممكن لكل نوع response ترجع status_code بحيث 400 لو الدنيامش  تمام إنما 200 لو الدنيا  تمام
            content= {
                "signal":result_signal
            }
        )

    # get the path of the project directory.
    project_directory_path =  ProjectController().get_project_path(project_id=project_id)
    file_path,file_id = data_controller.generate_unique_filepath( #we don't want to overwrite any existing files with the same name.
        original_file_name = file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path,"wb") as f: # إفتح الفايل ده بإستخدام ال aiofiles بطريقة async كتابة بالبايناري (wb==> Write Binary)
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE): # هيمشي Chunk by Chunk
                await f.write(chunk) # هيكتب ال Chunk إلي هو مسكه
    except Exception as e :

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    # دلوقتي الملف موجود فعليًا على الـ disk
    #لكن علشان ال app يعرف ان الملف موجود لازم يتخزن في ال Database
    # store the assets into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )


    asset_resource = Asset(
        asset_project_id=project.id, # الملف ده تابع لأي Project؟
        asset_type=AssetTypeEnum.FILE.value, # نوع ال asset هنا هو file
        asset_name=file_id, # ده اسم/ID الملف اللي اتحفظ على disk
        asset_size=os.path.getsize(file_path) # بتجيب حجم الملف بالـ bytes.
    )

    # Asset record is the record of the asset in the database (metadata about the file)
    asset_record = await asset_model.create_asset(asset=asset_resource) # حفظ الـ Asset في Database

    return JSONResponse(
        content={
            "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id" : file_id, # ده ال ID بتاع الملف إلي اتحفظ في ال Database

        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request,project_id:str,process_request:ProcessRequest):

    file_id = process_request.file_id #Ex: "file_123.txt"

    chunk_size = process_request.chunk_size #Ex: 1000

    overlap_size = process_request.overlap_size #Ex: 200

    do_reset = process_request.do_reset #Ex: 1

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                }
            )

        project_files_ids = {
            asset_record.id: asset_record.asset_name
        }

    else:

        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
        )

        project_files_ids = {
            record.id: record.asset_name
            for record in project_files
        }

    if len(project_files_ids) == 0: #there is no files to process for this project
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            }
        )

    # responsible for processing the files and generating chunks
    process_controller = ProcessController(project_id=project_id)

    num_records = 0
    num_files = 0

    # store the chunks into the database
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id( # delete all chunks related to this project
            project_id=project.id
        )

    for asset_id, file_id in project_files_ids.items():

        # {
        #     10: "file1.pdf",
        #     11: "file2.pdf"
        # }
        # أول iteration:
        # asset_id = 10
        # file_id = file1.pdf
        # الثاني:
        # asset_id = 11
        # file_id = file2.pdf


        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        # process the file content(document) into chunks
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
            )

        # store the chunks into the database
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id, #the project id to which the chunk belongs ( عشان تعرف الـ chunk ده تابع لأي project. )
                chunk_asset_id=asset_id # the asset id to which the chunk belongs. ( الـ chunk ده أصله أنهي ملف؟ )
            )
            for i, chunk in enumerate(file_chunks)
        ]

        # increase the number of records inserted into the database by the number of chunks inserted for this file
        num_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        num_files += 1 # increased by 1 for each file processed successfully

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": num_records,
            "processed_files": num_files
        }
    )
