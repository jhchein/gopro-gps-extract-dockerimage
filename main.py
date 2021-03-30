import argparse
import datetime
import json
import os
import subprocess

import ffmpeg
from azure.core.exceptions import ResourceExistsError
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobClient, ContainerClient

"""
Takes the URL (including SAS token) of a GoPro Video stored in a blob container,
extracts the creation date,
extracts GPS data from gopro video,
uploads the GPS data to another container (with creation date as folder) and
uploads the videos to another container (with creation date as folder)
"""

# CONFIG
local_video_filename = "input.mp4"
blob_account_url = "https://bikevideostorage.blob.core.windows.net"

# Login to Azure
tenant_id = os.environ.get("goprotenant_id")
client_id = os.environ.get("goproclient_id")
client_secret = os.environ.get("goproclient_secret")
credential = ClientSecretCredential(tenant_id, client_id, client_secret)


def parse_args():
    # ARG PARSE
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default=None)
    args = parser.parse_args()
    assert args.url is not None, "Please provide an 'url' including SAS token."
    return args


def main(args):
    input_blob = BlobClient.from_blob_url(args.url)
    _, filename = os.path.split(input_blob.blob_name)
    root, ext = os.path.splitext(filename)
    print(f"root: {root}")
    assert ext.lower() == ".mp4"

    gps_output_container = ContainerClient(
        account_url=blob_account_url, container_name="gpsdata", credential=credential
    )

    video_upload_container = ContainerClient(
        account_url=blob_account_url,
        container_name="inputvideos",
        credential=credential,
    )

    # Download blob into "input.mp4"
    print("Downloading video file")
    with open(local_video_filename, "wb") as fh:
        input_blob.download_blob().readinto(fh)

    # GET CREATION DATE FROM FILE
    print("Probing File")
    probe = ffmpeg.probe(filename="input.mp4")
    creation_time = probe["format"]["tags"]["creation_time"]
    creation_datetime = datetime.datetime.strptime(
        creation_time, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    print(f"Creation time: {creation_datetime}")

    # STORE JSON TO YYYY/DD/MM/GOPROFILENAME.JSON
    target_folder = os.path.join(
        str(creation_datetime.year),
        str(creation_datetime.month),
        str(creation_datetime.day),
    )
    gps_json_output_filename = os.path.join(target_folder, f"{root}.json")
    video_upload_filename = os.path.join(target_folder, f"{root}.MP4")
    print(f"JSON FILENAME: {gps_json_output_filename}")

    # Extract GPS data into gps_json_output_filename
    print("Extracting GPS data")
    result = subprocess.check_output("node process.js", shell=True)
    print(result)

    # Upload json file to gps data container
    try:
        with open("out.json", "rb") as fh:
            extracted_gps = json.load(fh)
            print("extraction successful")

        gps_output_blob = gps_output_container.upload_blob(
            name=gps_json_output_filename,
            data=json.dumps(extracted_gps),
            overwrite=True,
        )
        print(f"file '{gps_json_output_filename}' uploaded.")
        print(gps_output_blob.get_blob_properties())
    except ResourceExistsError:
        print("File already exists")

    # upload to inputvideos folder
    with open(local_video_filename, "rb") as data:
        length = os.path.getsize(local_video_filename)
        gps_output_blob = video_upload_container.upload_blob(
            name=video_upload_filename,
            data=data,
            length=length,
            overwrite=True,
        )


if __name__ == "__main__":
    args = parse_args()
    main(args)
