from datetime import datetime
import logging
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from azure.appconfiguration.provider import load
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import pandas as pd

from avi_helpers import Consts, VideoIndexerClient


app = func.FunctionApp()


@app.function_name(name="save_full_transcripts")
@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer", run_on_startup=True)
def save_full_transcripts(timer: func.TimerRequest) -> func.HttpResponse:
    logging.info(f"`save_full_transcript` function started at {datetime.now()}.")
    credential = DefaultAzureCredential()

    # Load configuration from Azure App Configuration
    endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
    logging.info("Loading configuration from Azure App Configuration.")
    logging.debug(f"Endpoint: {endpoint}")

    config = load(endpoint=endpoint, credential=credential)
    logging.info("Configuration loaded successfully.")
    logging.debug(f"Configuration: {config}")

    # Create Video Indexer Client & authenticate
    consts = Consts(
        config["AVIResourceName"],
        config["AVIResourceGroup"],
        config["AVISubscriptionID"],
    )
    avi_client = VideoIndexerClient()
    avi_client.authenticate_async(consts)
    logging.info("Authenticated with Video Indexer successfully.")

    # Create Blob Service & Container Clients
    blob_service_client = BlobServiceClient(
        config["TranscriptsStorageURL"], credential=credential
    )
    logging.info("Blob service client created successfully.")

    # Get the list of videos
    video_list = avi_client.list_videos_async()
    logging.info("Fetched video list successfully.")

    for video in video_list:
        # Get video details
        video_name = video["name"]
        video_id = video["id"]
        logging.info(f"Processing video: {video_name} with ID: {video_id}")

        # Check if the video is processed; if not, skip it
        if not avi_client.is_video_processed(video_id):
            logging.warning(f"Video {video_name} is not processed yet. Skipping.")
            continue

        # Check if the transcript already exists in the blob storage; if so, skip it
        file_name = f"{video_name}. txt"
        logging.info(f"Checking if transcript for {video_name} exists in blob storage.")

        blob_client = blob_service_client.get_blob_client(
            container=config["TranscriptsStorageContainerName"], blob=file_name
        )
        if blob_client.exists():
            logging.info(f"Transcript for {video_name} already exists. Skipping.")
            continue

        # Get full transcript from video
        video = avi_client.get_video_async(video_id)
        insights = video["videos"][0]["insights"]
        full_transcript = insights.get("transcript")

        # Format transcript
        transcript_elements = []
        for fragment in full_transcript:
            fragment_dict = {
                "text": fragment["text"],
                "start": fragment["instances"][0]["start"],
                "end": fragment["instances"][0]["end"],
            }
            transcript_elements.append(fragment_dict)

        transcript_df = pd.DataFrame(transcript_elements)
        file_text = f"Video Name: {video_name}\n"
        transcript_df["line"] = (
            transcript_df["start"]
            + " - "
            + transcript_df["end"]
            + ": "
            + transcript_df["text"]
        )
        file_text += "\n".join(transcript_df["line"].tolist())

        blob_client.upload_blob(data=file_text, overwrite=True)
        logging.info(
            f"Uploaded transcript for {video_name} to {blob_client.blob_name} in {blob_client.container_name}."
        )

    logging.info(f"`save_full_transcript` function completed at {datetime.now()}.")
