from typing import ClassVar, Dict
import random

from pdai.response import QAResponse, QAResponseCategory


class DVSMock:
    MOCK_SPACE: ClassVar[Dict] = QAResponseCategory.LABEL_SPACE

    def __init__(self):
        """
        To be implemented when needed.
        """
        pass

    @classmethod
    def generate_categories(cls, dvspondes: str, n: int):
        """
        Given a query produce n predictions.
        :param dvspondes:
        :param n:
        :return:
        """
        top_spaces = random.sample(list(cls.MOCK_SPACE.keys()), n)

        categories = []
        for top_cat in top_spaces:
            categories.append(
                # {
                #     "dvcat": top_cat,
                #     "dvdecod": random.choice(cls.MOCK_SPACE[top_cat]),
                #     "probability": random.random(),
                # }
                QAResponseCategory(
                    dvcat=top_cat,
                    dvdecod=random.choice(cls.MOCK_SPACE[top_cat]),
                    probability=random.random(),
                )
            )

        return QAResponse(dvspondes=dvspondes, categories=categories)
