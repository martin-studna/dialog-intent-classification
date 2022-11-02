from ..component import Component
from ..da import DAI, DA
from itertools import groupby
from collections import defaultdict


class GenericRuleDST(Component):
    def __call__(self, dial, logger):
        if dial['state'] is None:
            dial['state'] = dict()
        nlu: DA = dial['nlu']
        slot_value_p = [(x.slot, x.value, x.confidence)
                        for x in nlu.dais if x.slot != None]
        slot_value_p.sort(key=lambda x: tuple(map(str, x)))
        slot_value_p = [(slot, value, sum(map(lambda x: x[-1], x))) for (slot, value),
                        x in groupby(slot_value_p, key=lambda x: tuple(map(str, x[:-1])))]
        for slot, values in groupby(slot_value_p, key=lambda x: str(x[0])):
            # All the slots are initialized with { None: 1.0 }.
            if not slot in dial['state']:
                dial['state'][slot] = {None: 1.0}
            # Save the new slot into the state.
            conf = dial['state'][slot]
            # Get all values for the given slot.
            value_conf = {k: v for _, k, v in values}
            # Compute the probability of None  by substracting all other probabilities from 1.0.
            value_conf[None] = 1.0 - sum(value_conf.values())
            # Use the probability of None to multiply current values with it
            for key in set(value_conf.keys()).union(set(conf.keys())):
                conf[key] = conf.get(key, 0.0) * \
                    value_conf[None] + value_conf.get(key, 0.0)
            conf[None] = 0.0
            conf[None] = 1.0 - sum(conf.values())

        logger.info('State: %s', str(dial['state']))
        return dial
