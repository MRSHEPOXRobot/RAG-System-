from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId


#Design Custom validation on schema
class Project(BaseModel):

    id: Optional[ObjectId] = Field(None,alias="_id") #every schema should have an id field, alias="_id" means it will be stored as "_id" in MongoDB.

    project_id: str = Field(..., min_length=1) # ... means required field, min_length=1 means it should not be empty.

    @field_validator('project_id') #decorator to define a field validator (custom validation for project_id field)
    @classmethod #decorator to define a class method
    def validate_project_id(cls, value): #work on class method (cls==class) not instance method (self==instance)

        if not value.isalnum(): # isalpha_numeric(only letters and numbers)
            raise ValueError('project_id must be alphanumeric')

        return value

    #to ignore arbitrary types (like ObjectId) in Pydantic model.
    model_config = ConfigDict(
        arbitrary_types_allowed=True #allow arbitrary types (like ObjectId)
    )


    @classmethod #decorator to define a class method
    def get_indexes(cls): # define a class method to get indexes for the Project collection in MongoDB

        return [
            {
                "key": [
                    ("project_id", 1) #ascending order + mongoDB index on project_id field, -1 for descending order.
                ],
                "name": "project_id_index_1", # name of the index
                "unique": True #Unique project id without duplicates
            }
        ]
