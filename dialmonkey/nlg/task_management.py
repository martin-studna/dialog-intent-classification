from dialmonkey.component import Component
from dialmonkey.dialogue import Dialogue
from dialmonkey.da import DA, DAI
import yaml
import os
from itertools import groupby
import re
import random
from string import Formatter


class TaskManagementFormatter(Formatter):
    def __init__(self):
        super().__init__()

    def _format_task(self, task):
        tokens = task.split('|')
        sentence = ""
        if len(tokens) == 1:
            return tokens[0].split("=")[1]
        elif len(tokens) == 2:
            return tokens[0].split("=")[1] + " on " + tokens[1].split("=")[1]
        return task

    def format_field(self, value, format_spec):

        if format_spec == 'list':
            if not isinstance(value, list):
                value = value.split(',')
            if len(value) == 1:
                return self._format_task(value[0])
            return ', '.join([self._format_task(x) for x in value[:-1]]) + ' and ' + self._format_task(value[-1])
        return super().format_field(value, format_spec)


_placeholder_regex = re.compile(r'\{(\w+)\}')


def is_placeholder(string):
    if string is None:
        return False
    return _placeholder_regex.match(string) is not None


def simplify(x):
    if x is None:
        return None
    return x.lower()


def is_match(dai1: DAI, dai2: DAI):
    if dai1.intent != dai1.intent:
        return False
    if dai1.slot != dai2.slot:
        return False
    if is_placeholder(dai1.value) or is_placeholder(dai2.value):
        return True
    return simplify(dai1.value) == simplify(dai2.value)


def render_response(da: DA, matched_set):
    responses = []
    formatter = TaskManagementFormatter()
    for key, value in matched_set:
        gtda = DA.parse_cambridge_da(key)
        replacements = dict()
        for gtdai in gtda.dais:
            matched_dai = [dai for dai in da if is_match(dai, gtdai)]
            assert len(matched_dai) == 1  # Single dai can match single gt dai
            matched_dai = matched_dai[0]
            if is_placeholder(gtdai.value):
                replacements[gtdai.value[1:-1]] = matched_dai.value

        response = formatter.format(value, **replacements)
        responses.append(response)
    return ' '.join(responses)


def compute_da_priority(x):
    key, _ = x
    da = DA.parse_cambridge_da(key)
    return (len(da.dais), -sum(is_placeholder(x.value) for x in da.dais))


def prioritized_select(available_set):
    # Prioritize and select non-overlaping set of rules
    matched_set = []
    matched_set_da = set()
    matched_set_keys = []
    available_set.sort(key=compute_da_priority, reverse=True)
    for _, items in groupby(available_set, key=compute_da_priority):
        items = list(items)
        while len(items) > 0:
            item = random.choice(items)
            items.remove(item)
            key, value = item
            cda = DA.parse_cambridge_da(key)

            # Does the item have any collision with the matched set?
            if not any(any(is_match(dai1, dai2) for dai1 in cda) for da2 in matched_set_da for dai2 in da2):
                # No collision
                matched_set.append([item])
                matched_set_da.add(cda)
                matched_set_keys.append(key)
            elif key in matched_set_keys:
                # We have exact match
                # Adding the value as an alternative
                matched_set[matched_set_keys.index(key)].append(item)

    # For each group of items in the matched set select an random item
    matched_set = [random.choice(x) for x in matched_set]
    return matched_set


r = random.Random(42)


def build_nlg(templates):
    def intent_getter(x): return DA.parse_cambridge_da(x).dais[0].intent
    #templates = list(templates)
    # templates.sort(key=intent_getter)
    intent_lookup = {k: list(v)
                     for k, v in groupby(templates, key=intent_getter)}
    intent_lookup = {}
    for x in templates:
        if intent_getter(x) not in intent_lookup:
            intent_lookup[intent_getter(x)] = {}

        intent_lookup[intent_getter(x)][x] = templates[x]

    def lookup(da: DA):
        assert len(da.dais) > 0
        # We will support single intent
        assert len(set(x.intent for x in da.dais)) == 1

        # Prepare set of matched rules
        intent = da.dais[0].intent
        intent_set = intent_lookup[intent]
        intent_set = [(x, r.choice(intent_set[x])) for x in intent_set]
        available_set = []
        for key, value in intent_set:
            gtda = DA.parse_cambridge_da(key)
            is_matched = all(any(is_match(x, y) for x in da.dais)
                             for y in gtda.dais)
            if is_matched:
                available_set.append((key, value))

        matched_set = prioritized_select(available_set)

        # Return rendered response
        assert matched_set, "Could not find any matching template."
        return render_response(da, matched_set)

    return lookup


def read_templates(filename):
    with open(filename, 'r') as f:
        results = {}
        for line in f:
            line = line.rstrip()
            tokens = [token.replace('"', '') for token in line.split(":")]
            rest = ":".join(tokens[1:])
            tokens = [tokens[0], rest]
            if tokens[0] not in results:
                results[tokens[0]] = []
            results[tokens[0]].append("".join(tokens[1:]))
        return results


class TaskManagementNLG(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        default_filename = os.path.join(os.path.dirname(
            __file__), '../data/task_management-nlg-templates.yaml')
        self._nlg = build_nlg(read_templates(
            self.config.get('templates_file', default_filename)))

    def __call__(self, dial: Dialogue, logger):
        assert dial.action is not None

        logger.info(dial.action.to_cambridge_da_string())
        response = self._nlg(dial.action)
        dial.set_system_response(response)
        return dial
