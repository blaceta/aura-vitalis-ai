import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# Configuración de rutas
PATH_DOCUMENTOS = "./data"  # base de datos de informacion
PATH_CHROMA = "./chroma_db"       # La carpeta donde se guarda tu base de datos

def actualizar_base_datos():
    # 1. Limpieza preventiva: Borrar la base de datos vieja si existe
    if os.path.exists(PATH_CHROMA):
        print("Eliminando la base de datos antigua para evitar duplicados...")
        shutil.rmtree(PATH_CHROMA)
    
    # 2. Cargar todos los documentos de la carpeta
    print(f"Cargando documentos desde: {PATH_DOCUMENTOS}...")
    if not os.path.exists(PATH_DOCUMENTOS):
        os.makedirs(PATH_DOCUMENTOS)
        print(f"Creada la carpeta {PATH_DOCUMENTOS}. Por favor, coloca tus archivos .txt allí.")
        return

    loader = DirectoryLoader(PATH_DOCUMENTOS, glob="*.txt", loader_cls=TextLoader)
    documentos = loader.load()
    
    if not documentos:
        print("No se encontraron archivos .txt para procesar.")
        return

    # 3. Fragmentar el texto en bloques (Chunks)
    print("Segmentando el texto en bloques...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    bloques = text_splitter.split_documents(documentos)
    
    # 4. Crear y persistir la nueva base de datos vectorial
    print("Generando vectores y guardando en ChromaDB...")
    db = Chroma.from_documents(
        documents=bloques, 
        persist_directory=PATH_CHROMA
    )
    
    print(f"¡Éxito! Se han procesado {len(documentos)} archivos en {len(bloques)} bloques vectoriales.")

if __name__ == "__main__":
    actualizar_base_datos()
