from typing import List
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


app = FastAPI()


def get_db():
    MONGODB_URI = "mongodb+srv://estudiante:estudiante2024@clusterexfinal.k4mpd.mongodb.net/?retryWrites=true&w=majority&appName=ClusterExFinal"
    DATABASE = "estudiantes"
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE]
        yield db
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        client.close()


def get_collection():
    COLLECTION = "estudiantes"
    return COLLECTION


class Estudiante(BaseModel):
    id: str
    nombre: str
    apellido: str
    aprobado: bool
    nota: float
    fecha: datetime


class EstudianteCreate(BaseModel):
    nombre: str
    apellido: str
    aprobado: bool
    nota: float


@app.get("/api/v1/estudiantes", response_model=List[Estudiante])
def listar_estudiantes(db=Depends(get_db)) -> List[Estudiante]:
    estudiantes = db[get_collection()].find()
    return [
        Estudiante(
            id=str(estudiante["_id"]),
            nombre=estudiante["nombre"],
            apellido=estudiante["apellido"],
            aprobado=estudiante["aprobado"],
            nota=estudiante["nota"],
            fecha=estudiante["fecha"],
        )
        for estudiante in estudiantes
    ]


@app.get("/api/v1/estudiante/{estudiante_id}", response_model=Estudiante)
def buscar_estudiante(estudiante_id: str, db=Depends(get_db)) -> Estudiante:
    id = generar_object_id(estudiante_id)
    estudiante = db[get_collection()].find_one({"_id": id})
    if estudiante is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="No se ha encontrado al estudiante",
        )
    return Estudiante(
        id=str(estudiante["_id"]),
        nombre=estudiante["nombre"],
        apellido=estudiante["apellido"],
        aprobado=estudiante["aprobado"],
        nota=estudiante["nota"],
        fecha=estudiante["fecha"],
    )


@app.post("/api/v1/estudiante/create", response_model=Estudiante)
def crear_estudiante(estudiante: EstudianteCreate, db=Depends(get_db)) -> Estudiante:
    try:
        validar_nota(estudiante.nota)
        created_time = datetime.now()
        nuevo_estudiante = {
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "aprobado": estudiante.aprobado,
            "nota": estudiante.nota,
            "fecha": created_time,
        }
        result = db[get_collection()].insert_one(nuevo_estudiante)
        estudiante_creado = db[get_collection()].find_one({"_id": result.inserted_id})
        return Estudiante(
            id=str(estudiante_creado["_id"]),
            nombre=estudiante_creado["nombre"],
            apellido=estudiante_creado["apellido"],
            aprobado=estudiante_creado["aprobado"],
            nota=estudiante_creado["nota"],
            fecha=estudiante_creado["fecha"],
        )
    except HTTPException as he:
        print(f"Error: {he}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=he.detail,
        )
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Se produjo un error inesperado.",
        )


@app.put("/api/v1/estudiante/edit/{estudiante_id}", response_model=Estudiante)
def editar_estudiante(
    estudiante_id: str, estudiante: EstudianteCreate, db=Depends(get_db)
) -> Estudiante:
    try:
        id = generar_object_id(estudiante_id)
        validar_nota(estudiante.nota)
        estudiante_editado = {
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "aprobado": estudiante.aprobado,
            "nota": estudiante.nota,
        }
        response = db[get_collection()].update_one(
            {"_id": id}, {"$set": estudiante_editado}
        )
        if response.modified_count == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"No se ha encontrado al estudiante con id {estudiante_id}",
            )
        estudiante_editado = db[get_collection()].find_one({"_id": id})
        return Estudiante(
            id=str(estudiante_editado["_id"]),
            nombre=estudiante_editado["nombre"],
            apellido=estudiante_editado["apellido"],
            aprobado=estudiante_editado["aprobado"],
            nota=estudiante_editado["nota"],
            fecha=estudiante_editado["fecha"],
        )
    except HTTPException as he:
        print(f"Error: {he}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=he.detail,
        )
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Se produjo un error inesperado.",
        )


@app.delete("/api/v1/estudiante/delete/{estudiante_id}", response_model=Estudiante)
def borrar_estudiante(estudiante_id: str, db=Depends(get_db)) -> Estudiante:
    try:
        id = generar_object_id(estudiante_id)
        delete_result = db[get_collection()].delete_one({"_id": id})
        print(delete_result)
        if delete_result.deleted_count == 1:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content="El Estudiante se eliminó correctamente",
            )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"No se ha encontrado al estudiante con id {estudiante_id}",
        )
    except HTTPException as he:
        print(f"Error: {he}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=he.detail,
        )
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Se produjo un error inesperado.",
        )


def generar_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception as e:
        print(f"Error en el ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identificador (ID) inválido",
        )


def validar_nota(nota: float):
    if nota is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Por favor, ingrese una nota entre cero (0) y veinte (20).",
        )
    if nota < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nota no puede ser menor a cero (0).",
        )
    if nota > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nota no puede ser mayor a veinte (20).",
        )
