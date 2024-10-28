import os.path

from sklearn.exceptions import InconsistentVersionWarning
from sklearn.preprocessing import LabelEncoder
import joblib
from typing import Union, List
from spacy_sentence_bert.language import SentenceBert

from qaai.response import QAResponse, QAResponseCategory
from qaai.utils import normalize_text
import numpy as np

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

class QAPredictor:
    def __init__(
        self,
        models_file: str,
        dvcat_predict_name: str = "predict_proba",
        dvdecod_predict_name: str = "predict_proba",
        embeddings_model: str = "all-mpnet-base-v2",
    ):
        self._dvcat_model = None
        self._dvcat_encoder: LabelEncoder = None
        self._dvdecod_model = None
        self._dvdecod_encoder: LabelEncoder = None
        self.__load_models(models_file)

        self._dvcat_predict_name = dvcat_predict_name
        self._dvdecod_predict_name = dvdecod_predict_name
        self._embeddings_model = SentenceBert.get_model(embeddings_model)

    def __load_models(self, models_file: str):
        assert os.path.isfile(models_file), ValueError(
            f"No such models file {models_file}!"
        )
        models_dict = joblib.load(models_file)
        try:
            self._dvcat_model = models_dict["dvcat"]["model"]
            self._dvcat_encoder = models_dict["dvcat"]["encoder"]
        except KeyError:
            raise ValueError(
                f"DVCAT model or encoder not found. Expected key <dvcat> with subkeys <model> and <encoder>. Got {models_dict.keys()}"
            )

        try:
            self._dvdecod_model = models_dict["dvdecod"]["model"]
            self._dvdecod_encoder = models_dict["dvdecod"]["encoder"]
        except KeyError:
            raise ValueError(
                f"DVDECOD model or encoder not found. Expected key <dvdecod> with subkeys <model> and <encoder>. Got {models_dict.keys()}"
            )

    def encode(self, texts: List[str]):
        texts = [normalize_text(txt) for txt in texts]
        embeddings = self._embeddings_model.encode(texts)
        return embeddings

    def predict(
        self,
        prediction_input: Union[str, List[str]],
        batch_size: int = 10,
        num_predictions: int = 1,
    ):

        if isinstance(prediction_input, str):
            prediction_input = [prediction_input]

        predictions = []
        for i in range(0, len(prediction_input), batch_size):
            dvcat_chunk = [
                normalize_text(_input)
                for _input in prediction_input[i : i + batch_size]
            ]
            dvcat_embeddings = self.encode(dvcat_chunk)
            dvcat_predictor = getattr(self._dvcat_model, self._dvcat_predict_name)
            dvcat_predictions = dvcat_predictor(dvcat_embeddings)

            if num_predictions == 0:
                dvcat_predictions = self._dvcat_encoder.inverse_transform(
                    dvcat_predictions
                )
                dvcat_probabilities = (np.zeros_like(dvcat_predictions, dtype=np.float16)).flatten()
            else:
                dvcat_prediction_ids = np.argsort((-dvcat_predictions), axis=1)[
                    :, :num_predictions
                ]
                dvcat_probabilities = (dvcat_predictions[
                    np.expand_dims(np.arange(len(dvcat_predictions)), axis=1),
                    dvcat_prediction_ids,
                ]).flatten()
                dvcat_predictions = self._dvcat_encoder.inverse_transform(
                    dvcat_prediction_ids.flatten()
                )

            dvdecod_chunk = [
                f"{dvcat_predictions[i * num_predictions + j]}:{normalize_text(_input)}"
                for i, _input in enumerate(prediction_input)
                for j in range(num_predictions)
            ]

            dvdecod_embeddings = self.encode(dvdecod_chunk)
            dvdecod_predictor = getattr(self._dvdecod_model, self._dvdecod_predict_name)
            dvdecod_predictions = dvdecod_predictor(dvdecod_embeddings)

            if num_predictions == 0:
                dvdecod_predictions = self._dvdecod_encoder.inverse_transform(
                    dvdecod_predictions
                )
                dvdecod_probabilities = (np.zeros_like(
                    dvdecod_predictions, dtype=np.float16
                )).flatten()
            else:
                dvdecod_prediction_ids = self.dvdecod_validator(dvdecod_predictions, dvcat_prediction_ids)

                dvdecod_probabilities = (dvdecod_predictions[
                    np.expand_dims(np.arange(len(dvdecod_predictions)), axis=1),
                    dvdecod_prediction_ids,
                ]).flatten()

                dvdecod_predictions = self._dvdecod_encoder.inverse_transform(
                    dvdecod_prediction_ids
                )

            chunk_predictions = [
                {
                    "dvcat": dvcat_pred,
                    "dvcat_proba": dvcat_proba,
                    "dvdecod": dvdecod_pred,
                    "dvdecod_proba": dvdecod_proba,
                }
                for dvcat_pred, dvcat_proba, dvdecod_pred, dvdecod_proba in zip(
                    dvcat_predictions,
                    dvcat_probabilities,
                    dvdecod_predictions,
                    dvdecod_probabilities,
                )
            ]
            predictions.extend(chunk_predictions)

        predictions = [
            QAResponse(
                dvspondes=_inp,
                categories=[
                    QAResponseCategory(
                        dvcat=predictions[i * num_predictions + j]["dvcat"],
                        dvdecod=predictions[i * num_predictions + j]["dvdecod"],
                        probability=predictions[i * num_predictions + j]["dvcat_proba"],
                    )
                ],
            )
            for i, _inp in enumerate(prediction_input)
            for j in range(num_predictions)
        ]
        return predictions

    def dvdecod_validator(self, dvdecod_predictions, dvcat_prediction_ids):
        valid_dvdecodes = []
        dvcat_prediction = dvcat_prediction_ids.flatten()
        dvcat_labels = self._dvcat_encoder.inverse_transform(dvcat_prediction)

        for i, preds in enumerate(dvdecod_predictions):
            allowed_labels = QAResponseCategory.LABEL_SPACE[dvcat_labels[i]]

            for j in np.argsort(-preds):
                dvdecod_label = self._dvdecod_encoder.inverse_transform(np.array([j]))[0]
                if dvdecod_label in allowed_labels:
                    valid_dvdecodes.append([j])
                    break
        return valid_dvdecodes