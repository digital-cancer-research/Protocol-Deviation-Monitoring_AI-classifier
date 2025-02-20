import pytest

from pdai.prediction import QAPredictor

MODELS_FILE = "../models/models.joblib"

TEST_DATA = {
    "input_data": [
        "Description: Subject C011 taken at 11:05 but 2 hour ECG done at 13:13 and 4 hour ECG done at 18:09. ECGs also completed more than 5 minutes apart.Reason: For the 3 hour post-dose ECG the subject was sleeping. For the other ECGs. there were not completed as per protocol due to human error. Corrective action:CRA reminded site that ECGs must be performed as per protocol in the monitoring visit follow up email.",
        "The IMP vial could not be found during the visit. It was thought that it would have been disposed of after use on the 14Nov2017 but there was no record of destruction.The waste disposal bin used on the day of 14Nov2017 was traced however it had already been taken off-site for destruction. The bins are only destroyed once the level of radioactivity is below a certain level. In addition, it was calculated that only 0.18mBq of residual IMP activity was left in the vial. However, as per the protocol, if there is any IMP Solution for Injection left after the administration this should be retained for six months as per GMP requirements in an appropriate controlled storage area at ≤ 25°C. The documentation for the batch, including the order form, certificate of release, dispatch and delivery notes, record of receipt and accountability was available for review.",
    ],
    "dvcats": [
        "WRONG STUDY TREATMENT/ADMINISTRATION/DOSE",
        "ASSESSMENT OR TIME POINT COMPLETION",
    ],
    "dvdecods": [
        "OTHER DEVIATION RELATED TO WRONG STUDY TREATMENT/ADMINISTRATION/DOSE",
        "MISSED ASSESSMENT - OTHER",
    ],
}

pytestmark = pytest.mark.parametrize("input_data", [TEST_DATA["input_data"]])


@pytest.fixture
def predictor():
    """Returns a QAPredictor instance"""
    return QAPredictor(models_file=MODELS_FILE)


@pytest.fixture
def predictions(input_data, predictor):
    predictions = predictor.predict(prediction_input=input_data)
    return predictions


@pytest.mark.parametrize("dvcats", [TEST_DATA["dvcats"]])
def test_dvcat(predictions, dvcats):
    assert predictions[0].categories[0].dvcat == dvcats[0]


@pytest.mark.parametrize("dvdecods", [TEST_DATA["dvdecods"]])
def test_dvdecod(predictions, dvdecods):
    assert predictions[1].categories[0].dvdecod == dvdecods[1]
