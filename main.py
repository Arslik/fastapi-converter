import logging
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import os
from io import BytesIO
from typing import Annotated

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_video_from_image(image_path, output_path, duration, fps=1):
    logger.info(f"Reading image from {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width, layers = image.shape
    num_frames = int(duration * fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    logger.info(f"Creating video with {num_frames} frames")
    for _ in range(num_frames):
        video.write(image)

    video.release()
    logger.info(f"Video created at {output_path}")


@app.post("/convert")
async def convert_image_to_video(
        file: UploadFile = File(...),
        duration: int = Form(...),
        fps: int = Form(...)
):
    print("Received request to convert image to video")
    input_path = f"temp_{file.filename}"
    output_path = "output.mp4"

    try:
        print(f"Saving uploaded file to {input_path}")
        with open(input_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        print(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")

    try:
        print("Converting image to video")
        create_video_from_image(input_path, output_path, duration, fps)
    except Exception as e:
        print(f"Error converting image to video: {e}")
        raise HTTPException(status_code=500, detail=f"Error converting image to video: {str(e)}")

    try:
        print(f"Reading video file from {output_path}")
        with open(output_path, "rb") as video_file:
            video_bytes = BytesIO(video_file.read())
    except Exception as e:
        print(f"Error reading video file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading video file: {str(e)}")

    try:
        print("Cleaning up temporary files")
        os.remove(input_path)
        os.remove(output_path)
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")

    print("Returning video as response")
    return StreamingResponse(video_bytes, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
