"""
Script para configurar Azure Blob Storage
"""
import os
from azure.storage.blob import BlobServiceClient

def setup_azure_storage():
    """Configurar Azure Blob Storage y crear contenedores necesarios"""
    
    # Obtener credenciales de las variables de entorno
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
    
    if not account_name or not account_key:
        print("❌ Error: Variables de entorno de Azure Storage no configuradas")
        print("Necesitas configurar:")
        print("- AZURE_STORAGE_ACCOUNT_NAME")
        print("- AZURE_STORAGE_ACCOUNT_KEY")
        return False
    
    try:
        # Crear cliente de Azure Blob Storage
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=account_key
        )
        
        # Crear contenedor si no existe
        try:
            blob_service_client.create_container(container_name)
            print(f"✅ Contenedor '{container_name}' creado exitosamente")
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                print(f"ℹ️  Contenedor '{container_name}' ya existe")
            else:
                print(f"❌ Error creando contenedor: {e}")
                return False
        
        # Crear subcarpetas
        subfolders = ['media', 'static']
        for folder in subfolders:
            try:
                # Crear un blob vacío para representar la carpeta
                blob_client = blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=f"{folder}/.keep"
                )
                blob_client.upload_blob("", overwrite=True)
                print(f"✅ Carpeta '{folder}' configurada")
            except Exception as e:
                print(f"⚠️  Advertencia creando carpeta '{folder}': {e}")
        
        print("\n🎉 Azure Blob Storage configurado correctamente!")
        print(f"📁 Contenedor: {container_name}")
        print(f"🌐 URL base: https://{account_name}.blob.core.windows.net/{container_name}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Azure Storage: {e}")
        return False

if __name__ == "__main__":
    setup_azure_storage()
