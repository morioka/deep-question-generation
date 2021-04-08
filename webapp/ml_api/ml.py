from random import choice
from time import sleep

class MockMLAPI:
    def __init__(self):
        # model instanse
        self.model = None

    def load(self, filepath=''):
        """
        when server is activated, load weight or use joblib or pickle for performance improvement.
        then, assign pretrained model instance to self.model.
        """
        sleep(20)
        pass

    def predict(self, x):
        """implement followings
        - Load data
        - Preprocess
        - Prediction using self.model
        - Post-process
        """
        sleep(10)
        preds = [choice(['happy', 'sad', 'angry']) for i in range(len(x))]
        out = [{'text': t.text, 'sentiment': s} for t, s in zip(x, preds)]
        return out
