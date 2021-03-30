# Gopro GPS Extract Docker image

The repository creates a Docker image to extract GPS data from GoPro mp4 files stored in an Azure Blob Storage.

It is part of a larger Microsoft Azure-based project to extract GPS data from GoPro Video files, creates a video overlay with metrics (such as speed, heart rate) and encodes the video in h264 for further processing.

Feel free to take, replace, and/or remove parts of this code for your own purpose, if you do not want to use (some of the) Azure Services or Docker.

## Requirements

* A GoPro mp4 file stored in any Azure Blob Storage (or ADLS Gen 2 respectively)
* An Azure Storage account with two containers: ```gpsdata``` (for GPS data) and ```inputvideos``` (for archiving the video)
* A Service Principal with at least 'Blob Data Contributor' role assignment to the two containers (you want write access)
* An Azure Container Registry (to store and provide the image)
* Docker (for building the image)

## Steps

### (Optional) add the Service Pricipal Secrets to your environment

* tenant_id -> goprotenant_id
* client_id -> goproclient_id
* client_secret -> goproclient_secret

### Create the image

If you run Windows and added the secrets to your environment, you might want to edit and run 'build_docker.bat' with your own configuration, otherwise follow these steps:

* Login to your container registry ```az acr login --name myregistry```

* Build the image. If you added the secrets to your environment, you can use the following command, otherwise replace the variables (e.g. ```%goproclient_id%```) with your own Service Principal secrets. ```docker image build --build-arg tenant_id=%goprotenant_id% --build-arg client_id=%goproclient_id% --build-arg client_secret=%goproclient_secret% -t myregistry.azurecr.io/goproextraction .```
* Push the image to your registry ```docker push myregistry.azurecr.io/goproextraction```

### Run the extraction

* Create an URL (including SAS Token if the blob requires authentication) that points towards the input video file
* run the extraction ```docker run -t myregistry.azurecr.io/goproextraction --url BLOB-URL-INCLUDING-SAS-TOKEN --storageaccountname THE-NAME-OF-YOUR-STORAGE-ACCOUNT```

### Check the output

The videos will be uploaded to ```inputvideos/yyyy/MM/DD/filename.mp4``` while GPS files will go to ```gpsdata/yyyy/MM/DD/filename.json```

## Troubleshooting / known issues

* The extraction will freeze when storage account does not exist.
