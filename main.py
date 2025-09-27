from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, computed_field
import json

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[int, Field(...,gt=0, description="The ID must be a positive integer")]
    name:Annotated[str, Field(...,min_length=1, description="Name must be a non-empty string")]
    age: Annotated[int, Field(...,gt=0, description="Age must be a positive integer")]
    gender:Annotated[ Literal['male', 'female', 'other'], Field(...,description="Gender must be 'male', 'female', or 'other'")]
    email: Annotated[str, Field(description="Email must be a valid email address")]
    phone: Annotated[str, Field(description="Phone number must be a valid phone number")]
    address: str
    medical_history: list[str]
    allergies: list[str]
    blood_type: Annotated[str, Field(...,description="Blood type must be one of A+, A-, B+, B-, AB+, AB-, O+, O-")]
    height_cm: Annotated[float, Field(...,gt=0, description="Height must be a positive number in cm")]
    weight_kg: Annotated[float, Field(...,gt=0, description="Weight must be a positive number in kg")]

    @computed_field
    @property
    def bmi(self) -> float:
        height_m = self.height_cm / 100
        return round(self.weight_kg / (height_m ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None, min_length=1, description="Name must be a non-empty string")]
    age: Annotated[Optional[int], Field(default=None, gt=0, description="Age must be a positive integer")]  
    gender: Annotated[Optional[Literal['male', 'female', 'other']], Field(default=None)]
    email: Annotated[Optional[str], Field(default=None, description="Email must be a valid email address")]
    phone: Annotated[Optional[str], Field(default=None, description="Phone number must be a valid phone number")]
    address: Optional[str] = None
    medical_history: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
    blood_type: Annotated[Optional[str], Field(default=None, description="Blood type must be one of A+, A-, B+, B-, AB+, AB-, O+, O-")]
    height_cm: Annotated[Optional[float], Field(default=None, gt=0, description="Height must be a positive number in cm")]
    weight_kg: Annotated[Optional[float], Field(default=None, gt=0, description="Weight must be a positive number in kg")]


def load_data():
    with open('patient.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patient.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get('/about')
def about():
    return {"message": "A fully functional API to manage your patient records."}

@app.get('/patients')
def get_patients():
    data = load_data()
    return data

@app.get('/patients/{patient_id}')
def get_patient(patient_id: int = Path(..., description="The ID of the patient to retrieve", example=1)):
    data = load_data()
    for patient in data:
        if patient['id'] == patient_id:
            return patient
    # return {"error": "Patient not found"}
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of age , blood type'), order: str = Query('asc', description='Order can be asc or desc')):
    # ... means required parameter and order by default is asc and optional parameter
    valid_fields = ['age', 'blood_type']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    data = load_data()
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data, key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    # reverse = (order == 'desc')
    # sorted_data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)
    return sorted_data





# @app.post('/create-patient')
# def add_patient(patient: dict):
#     data = load_data()
#     data.append(patient)
#     with open('patient.json', 'w') as f:
#         json.dump(data, f, indent=4)
#     return {"message": "Patient added successfully"}


@app.post('/create-patient')
def add_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    # if patient.id in data:
    #     raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    for existing_patient in data:
        if existing_patient['id'] == patient.id:
            raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    # new patient add to database
    #  pydantic model to dict
    # data[patient.id] = patient.model_dump(exclude=['id']) if json file in key value pair
    data.append(patient.model_dump())


    # save updated data
    save_data(data)
    # return {"message": "Patient added successfully"}
    return JSONResponse(status_code=201, content={"message": "Patient added successfully"})




@app.put('/update/{patient_id}')
def update_patient(patient_id: int, updated_info: PatientUpdate):
    data = load_data()

    if patient_id not in [patient['id'] for patient in data]:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # existing patient info = data[patient_id] # if json file in key value pair
    existing_patient_info  =data[[patient['id'] for patient in data].index(patient_id)]

    updated_data = updated_info.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        existing_patient_info[key] = value

    # existing patient info -> pydantic object -> upadate bmi and verdict -> pydantic obj -> dict -> save
    # existing_patient_info['id'] = patient_id 
    patient_pydantic_obj = Patient(**existing_patient_info)

    # pydantic obj -> dict
    existing_patient_info = patient_pydantic_obj.model_dump()

    #  add this dict to data
    data[[patient['id'] for patient in data].index(patient_id)] = existing_patient_info

    # save updated data
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})




@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: int):
    data = load_data()

    if patient_id not in [patient['id'] for patient in data]:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_idd = [patient['id'] for patient in data]
    del data[patient_idd.index(patient_id)]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})
    # for i, patient in enumerate(data):
    #     if patient['id'] == patient_id:
    #         del data[i]
    #         save_data(data)
    #         return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})
    # raise HTTPException(status_code=404, detail="Patient not found")




# @app.put('/patients/{patient_id}')
# def update_patient_alt(patient_id: int, updated_info: dict):
#     data = load_data()
#     for patient in data:
#         if patient['id'] == patient_id:
#             patient.update(updated_info)
#             with open('patient.json', 'w') as f:
#                 json.dump(data, f, indent=4)
#             return {"message": "Patient updated successfully"}
#     return {"error": "Patient not found"}

# @app.delete('/patients/{patient_id}')
# def delete_patient_alt(patient_id: int):
#     data = load_data()
#     for i, patient in enumerate(data):
#         if patient['id'] == patient_id:
#             del data[i]
#             with open('patient.json', 'w') as f:
#                 json.dump(data, f, indent=4)
#             return {"message": "Patient deleted successfully"}
#     return {"error": "Patient not found"}


# To run the FastAPI application, use the following commands in your terminal:
# python -m venv myenv
# myenv/Scripts/activate
# pip install fastapi uvicorn pydantic
# uvicorn main:app --reload


