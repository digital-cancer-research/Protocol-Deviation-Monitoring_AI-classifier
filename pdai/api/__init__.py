import os.path
from typing import List

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from types import SimpleNamespace

from PDMAIC.pdai.prediction import QAPredictor
from PDMAIC.pdai.response import QAResponse
import os

MODELS_FILE = os.path.join(os.path.dirname(__file__), "../../models/models.joblib")

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)
context = SimpleNamespace()

@app.on_event("startup")
def app_startup():
    if not os.path.isfile(MODELS_FILE):
        raise FileNotFoundError(f"Missing models at {MODELS_FILE}")

    context.predictor = QAPredictor(models_file=MODELS_FILE)


@app.get("/")
@app.post("/")
def read_root():
    raise HTTPException(
        status_code=404,
        detail="You seem to have lost your way. There is nothing here to see!",
    )

@app.post("/prediction", response_model=List[QAResponse])
def predict_protocol_deviation(
    body: dict = Body(...),
):
    """
    Endpoint for predictions.
    :param body: Two fields expected: query[str] and num_predictions[int].
    :return:
    """
    try:
        query = body["query"]
        num_predictions = int(body.get("num_predictions", 1))
        if num_predictions <= 0 or num_predictions > 64:
            raise HTTPException(
                status_code=400,
                detail=f"Unprocessable request data: 'num_predictions' must be a positive integer "
                       f"and less than or equal to 64, but received {body['num_predictions']}.",
                headers= {"X-Error":f"AI tool returned an error: invalid or incorrectly formatted num_predictions value."
                              f"Request body: {body}"}
            )
        qa_response = context.predictor.predict(query, num_predictions=num_predictions)
        return qa_response
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=(f"Unprocessable request data {body}. "
                   f"Two fields expected: query[str] and num_predictions[int]. "
                   f"Details: {str(e)}"),
            headers= {"X-Error":f"AI tool returned an error: {str(e)}"
                          f"Request body: {body}"})
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to obtain prediction for {body}. Details: {str(e)}",
            headers= {"X-Error":f"AI tool returned an error: {str(e)}"
                          f"Request body: {body}"})


@app.post("/prediction/dvdecod", response_model=List[QAResponse])
def protocol_deviation_code_list_per_category(body: dict = Body(...),):
    try:
        dvcode = body["dvcode"]
        query = body["query"]
        num_predictions = int(body.get("num_predictions", 1))
        if num_predictions <= 0 or num_predictions > 64:
            raise HTTPException(
                status_code=400,
                detail=f"Unprocessable request data: 'num_predictions' must be a positive integer "
                       f"and less than or equal to 64, but received {body['num_predictions']}.",
                headers= {"X-Error":f"AI tool returned an error: invalid or incorrectly formatted num_predictions value."
                              f"Request body: {body}"}
            )
        qa_response = context.predictor.codes(dvcode, query, num_predictions=num_predictions)
        return qa_response

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unprocessable request data {body}. \n One field expected: dvcode.",
            headers= {"X-Error":f"AI tool returned an error: {str(e)} \n Request body: {body}"})

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unprocessable request data {body}. \n One field expected: dvcode.",
            headers= {"X-Error":f"AI tool returned an error: {str(e)} \n Request body: {body}"})

