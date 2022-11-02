from dialmonkey.da import DA
from dialmonkey.component import Component
from hw4.da_classifier import IntentSlotClassifier


class DSTC2NLU(Component):
    """A restaurant NLU."""

    def __init__(self, config=None):
        self.model = IntentSlotClassifier(
            batch_normalization=True, hidden_layers=[800, 800], batch_size=32)
        self.model.train(epochs=10)

    def __call__(self, dial, logger):
        da = self.model.predict(dial.user)

        for dai in da.dais:
            dial.nlu.append(dai)

        logger.info('NLU: %s', str(dial.nlu))
        return dial
