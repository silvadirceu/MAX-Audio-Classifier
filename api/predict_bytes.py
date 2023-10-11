#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
from core.model import ModelWrapper
from flask_restplus import fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from maxfw.core import MAX_API, PredictAPI
from utils.serializers import bytes_to_ndarray
from config import SPEECH_IDX, NOISE_IDX, SILENCE_IDX, SINGING_IDX, INSTRUMENTAL_IDX, MUSIC_IDX
import numpy as np

# set up parser for audio input data
input_parser = MAX_API.parser()
input_parser.add_argument(
    "audio",
    type=FileStorage,
    location="files",
    required=True,
    help="signed 16-bit PCM WAV audio file",
)
input_parser.add_argument(
    "start_time",
    type=float,
    default=0,
    help="The number of seconds into the audio file the prediction should start at.",
)
input_parser.add_argument(
    "topN",
    type=int,
    default=5,
    help="The  most probable topN classes.",
)
input_parser.add_argument(
    "filter",
    required=False,
    action="split",
    help="List of labels to filter (optional)",
)

label_prediction = MAX_API.model(
    "LabelPrediction",
    {
        "label_id": fields.Integer(required=False, description="Label identifier"),
        "label": fields.String(required=True, description="Audio class label"),
        "probability": fields.Float(required=True),
    },
)

music_probability= MAX_API.model(
    "MusicProbability",
    {
        "probability": fields.Float(required=True),
    },
)

resume_music_score= MAX_API.model(
    "MusicScore",
    {
        "score": fields.Float(required=True),
    },
)

resume_music_labels= MAX_API.model(
    "MusicLabel",
    {
        "label": fields.String(required=True),
    },
)

predict_response = MAX_API.model(
    "ModelPredictResponse",
    {
        "status": fields.String(required=True, description="Response status message"),
        "predictions": fields.List(
            fields.Nested(label_prediction),
            description="Predicted audio classes and probabilities",
        ),
        "music_score": fields.List(
            fields.Nested(music_probability),
            description="Music Probability",
        ),
        "resume_scores": fields.List(
            fields.Nested(resume_music_score),
            description="Music scores",
        ),
        "resume_labels": fields.List(
            fields.Nested(resume_music_labels),
            description="Music Labels",
        ),
    },
)



class ModelBytesPredictAPI(PredictAPI):
    model_wrapper = ModelWrapper()

    @MAX_API.doc("predict")
    @MAX_API.expect(input_parser)
    @MAX_API.marshal_with(predict_response)
    def post(self):
        """Predict audio classes from input data"""
        result = {"status": "error"}

        args = input_parser.parse_args()
        # Decode the base64 audio data
        try:
            audio_bytes = args["audio"].read()
        except Exception as e:
            e = BadRequest()
            e.data = {
                "status": "error",
                "message": str(e),
            }
            raise e
        
        audio_data = bytes_to_ndarray(audio_bytes)
        
        # Getting the predictions
        try:
            preds, music_score = self.model_wrapper._predict(audio_data, args["start_time"], args["topN"])
        except ValueError:
            e = BadRequest()
            e.data = {
                "status": "error",
                "message": "Invalid start time: value outside audio clip",
            }
            raise e

        # Aligning the predictions to the required API format
        label_preds = [
            {"label_id": p[0], "label": p[1], "probability": p[2]} for p in preds
        ]
        
        # Filter list
        if args["filter"] is not None and any(x.strip() != "" for x in args["filter"]):
            label_preds = [x for x in label_preds if x["label"] in args["filter"]]

        #resume features
        resume_labels = np.array([
                        'music',
                        'instrumental',
                        'singing',
                        'speech',
                        'silence',
                        'noise'
                        ])
            
        resume_scores = np.zeros((6,))

        for c in range(len(label_preds)):
            if label_preds[c]["label_id"] in MUSIC_IDX:
                resume_scores[0] += label_preds[c]["probability"]
            elif label_preds[c]["label_id"] in INSTRUMENTAL_IDX:
                resume_scores[1] += label_preds[c]["probability"]
            elif label_preds[c]["label_id"] in SINGING_IDX:
                resume_scores[2] += label_preds[c]["probability"]
            elif label_preds[c]["label_id"] in SPEECH_IDX:
                resume_scores[3] += label_preds[c]["probability"]
            elif label_preds[c]["label_id"] in SILENCE_IDX:
                resume_scores[4] += label_preds[c]["probability"]
            elif label_preds[c]["label_id"] in NOISE_IDX:
                resume_scores[5] += label_preds[c]["probability"]

        music_prob = {"probability": music_score}

        idx_sort = np.argsort(resume_scores)[::-1]
        
        res_scores = [{"score": s} for s in list(resume_scores[idx_sort])]
        res_labels = [{"label": l} for l in list(resume_labels[idx_sort])]
        
        result["predictions"] = label_preds
        result["status"] = "ok"
        result["music_score"] = music_prob
        result["resume_scores"] = res_scores
        result["resume_labels"] = res_labels

        return result