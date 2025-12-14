import base64
import os
import uuid


def should_record_video(driver, is_browserstack: bool) -> bool:
    """Decide whether local video recording should run."""
    return driver is not None and not is_browserstack


def build_unique_video_name(test_name: str, retry_count: int) -> str:
    """Create a unique identifier for the recorded video."""
    sanitized_name = test_name.replace("/", "_").replace(":", "_")
    return f"{sanitized_name}_{retry_count}_{uuid.uuid4().hex[:8]}"


def save_recording(driver, folder: str, unique_id: str) -> str:
    """Stop the recording, persist it to disk, and return the file path."""
    video_raw = driver.stop_recording_screen()
    os.makedirs(folder, exist_ok=True)
    video_file = os.path.join(folder, f"{unique_id}.mp4")
    with open(video_file, "wb") as file:
        file.write(base64.b64decode(video_raw))
    return video_file
