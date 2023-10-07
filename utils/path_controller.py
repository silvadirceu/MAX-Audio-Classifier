import os
from fastapi import HTTPException
from services.settings import settings


def audio_path(details):
    ext = os.path.basename(details["audio_filename"]).split(".")[-1]

    if details["is_task"]:
        audio_path = os.path.join(
            settings.AUDIO_TASKS_DIR,
            details["work_id"],
            details["track_id"] + "." + ext,
        )
    else:
        audio_path = os.path.join(
            settings.AUDIO_UNIVERSE_DIR,
            details["work_id"],
            details["track_id"] + "." + ext,
        )

    if os.path.exists(audio_path):
        return audio_path
    else:
        try:
            return HTTPException(
                status_code=404,
                detail="Audio file could not be found in database for path: {}.".format(
                    audio_path
                ),
            )
        except:
            return {
                "status_code": 404,
                "detail": "Audio file could not be found in database for path: {}.".format(
                    audio_path
                ),
            }


def output_path(details):
    file_output_path = ""
    if details["is_task"]:
        file_output_path = os.path.join(
            settings.TASK_DIR,
            details["work_id"],
            details["track_id"] + "." + settings.FILE_EXT,
        )
        if not os.path.exists(os.path.join(settings.TASK_DIR, details["work_id"])):
            os.makedirs(os.path.join(settings.TASK_DIR, details["work_id"]))
    else:
        file_output_path = os.path.join(
            settings.UNIVERSE_DIR,
            details["work_id"],
            details["track_id"] + "." + settings.FILE_EXT,
        )
        if not os.path.exists(os.path.join(settings.UNIVERSE_DIR, details["work_id"])):
            os.makedirs(os.path.join(settings.UNIVERSE_DIR, details["work_id"]))

    return file_output_path
