from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import os
import pathlib
import uuid

key = 'DefaultEndpointsProtocol=https;AccountName=blobstorageforstylecard;AccountKey=iXcK8Uf12x4UMKh+FkG8SLEkAcypmpbUoYRAgt4hrOPY/Ex/CK7i497g78NsU6KCtPBuKRdVYhEGnoZ31n5QRQ==;EndpointSuffix=core.windows.net'
container_name = 'product-images'

blob_service_client = BlobServiceClient.from_connection_string(key)

def add_blob_to_container(blob_data):
    local_path = "./data"
    local_file_name = "imageBlob"+str(uuid.uuid4())+".txt"
    upload_file_path = os.path.join(local_path, local_file_name)

    file = open(upload_file_path, 'w')
    file.write(str(blob_data))
    file.close()

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
    with open(upload_file_path, "rb") as data:
        print("Uploading Blob Data")
        blob_client.upload_blob(data)
    os.remove(upload_file_path)

    return "https://blobstorageforstylecard.blob.core.windows.net/product-images/"+local_file_name