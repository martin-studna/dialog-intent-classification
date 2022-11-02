from dialmonkey.component import Component
from dialmonkey.da import DAI, DA
from itertools import chain
from dialmonkey.repositories import SolarRepository
from collections import deque
from itertools import starmap
import re


def create_intent_formatter(intent, **default_slots):
    def formatter(**x):
        args = [f'{k}={v}' if v != '' else f'{k}' for k,
                v in chain(default_slots.items(), x.items())]
        return f"{intent}({','.join(args)})"
    return formatter


def regex_parser(reg, formatter):
    expr = re.compile(reg)

    def call(x):
        match = expr.match(x)
        if match:
            if callable(formatter):
                return formatter(**match.groupdict())
            else:
                return formatter
        return None
    return call


def Sequential(*parsers):
    def call(x):
        for f in parsers:
            result = f(x)
            if result is not None:
                return result
        return None
    return call


def simplify(x):
    x = x.lower()
    words = []
    strip_chars = [',', '.', '!', '?', '"', "'", ';']
    for w in x.split():
        append_end = []
        for ch in strip_chars:
            if w.startswith(ch):
                words.append(ch)
            if w.endswith(ch):
                append_end.append(ch)
            w = w.strip(ch)
        words.append(w)
        append_end.reverse()
        words.extend(append_end)
    x = ' '.join(words)

    x = x.replace('n\'t', ' not').replace('\'m', ' am')
    x = re.sub(r'(^|\s)our planet($|\s)',
               lambda m: m.group(1) + 'earth' + m.group(2), x)
    x = re.sub(r'(^|\s)largest($|\s)', lambda m: m.group(
        1) + 'biggest' + m.group(2), x)
    x = re.sub(r'(^|\s)larger($|\s)', lambda m: m.group(
        1) + 'bigger' + m.group(2), x)
    x = re.sub(r'(^|\s)us($|\s)', lambda m: m.group(
        1) + 'earth' + m.group(2), x)
    return x

# Builds a function which replaces known words with tokens


def build_tokenize(repo: SolarRepository):
    objectRegex = re.compile(r'(?:^|\s)(' + "|".join([re.escape(simplify(
        x['englishName'])) for x in repo.bodies() if x['englishName']]) + r')(?:$|\s)')

    def tokenize(x):
        matches = []

        def map_match(x):
            def fn(match):
                matches.append(match.group(1))
                return match.group(0).replace(match.group(1), x)
            return fn
        x = objectRegex.sub(map_match('<object>'), x)
        return x, matches
    return tokenize

# Build the parser used to parse the expression


def build_parser():
    free_start = r'^(?:.*\s|)'
    free_end = r'(?:\s.*|)$'
    day = r"today|tomorrow|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    time = r'([0-9]{1,2}[.:][0-9]{1,2})|([0-9]{1,2}\s*[ap]m)'
    date = rf"(({day})|({time}))"
    fr = r'(?:\s.*|)'
    article = r'(?:\s*)(?:a|an|the)?(?:\s*)'

    def map_object(x):
        return x.replace(' ', '_')
    return Sequential(
        # Get tasks
        regex_parser(free_start + rf'(?:if|whether|do){fr} i{fr} have{fr} any{fr} (?:plans|meetings|tasks|events){fr} (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda time, **k: f'get_tasks(time={time})'),
        regex_parser(free_start + rf'(?:get){fr} (?:plans|events|tasks|meetings|goals){fr} (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda time, **k: f'get_tasks(time={time})'),


        # Create task
        regex_parser(free_start + rf'(?:schedule|plan|prepare|arrange|create){article} (?P<name>[^\s]+){fr} (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda name, time, **k: f'create_task(name={name},time={time})'),
        regex_parser(free_start + rf'(?:schedule|plan|prepare|arrange|create){article} (?P<name>[^\s]+)' + \
                     free_end, lambda name, **k: f'create_task(name={name})'),


        # Delete task
        regex_parser(free_start + rf'(?:delete|remove|cancel|erase|dismiss|detach|(take\s+away)|(take\s+off)|){article} (?P<name>[^\s]+) (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda name, time, **k: f'delete_task(name={name},time={time})'),
        regex_parser(free_start + rf'(?:delete|remove|cancel|erase|dismiss|detach|(take\s+away)|(take\s+off)|){article} (?P<name>[^\s]+)' + \
                     free_end, lambda name, **k: f'delete_task(name={name})'),


        # Delete all tasks for specific time
        regex_parser(free_start + rf'(?:delete|remove|cancel|erase|dismiss|detach|(take\s+away)|(take\s+off)|){fr} (?:plans|meetings|tasks|events){fr} (?:scheduled|planned|arranged){fr} (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda time, **k: f'delete_tasks(time={time})'),
        regex_parser(free_start + rf'(?:delete|remove|cancel|erase|dismiss|detach|(take\s+away)|(take\s+off)|){fr} (?:plans|meetings|tasks|events){fr} (?:for|at|on|in){fr} (?P<time>{date})' + \
                     free_end, lambda time, **k: f'delete_tasks(time={time})'),


        # Get task information
        regex_parser(
            free_start + rf'about{article} (?P<name>[^\s]+) (?:for|at|on|in){fr} (?P<time>{date})' + free_end, lambda name, time, **k: f'get_task(name={name}, time={time})'),
        regex_parser(
            free_start + rf'about{article} (?P<name>[^\s]+)' + free_end, lambda name, **k: f'get_task(name={name})'),


        # Request property
        regex_parser(
            free_start + rf'when{fr} is{article}(?P<name>[^\s]+)' + free_end, lambda name, **k: f'request_property(name={name},time)'),
        regex_parser(
            free_start + rf'where{fr} is{article}(?P<name>[^\s]+)' + free_end, lambda name, **k: f'request_property(name={name},place)'),

        # Count tasks
        regex_parser(
            free_start + rf'How{fr} many{fr} are{fr} (?:for|at|on|in){fr} (?P<time>{date})' + free_end, lambda time, **k: f'count(time={time})'),

        # Greet
        regex_parser(free_start + rf'(?:hi|hello)' + free_end, 'greet()'),
        regex_parser(free_start + rf'(?:ask you)' + \
                     free_end, 'question_request()'),
        regex_parser(free_start + rf'(?:thanks|thank)' + \
                     free_end, 'request_more()'),
        regex_parser(free_start + rf'(?:ok|goodbye|that is all|good bye)' + \
                     free_end, 'goodbye()'),
    )


class TaskManagementNLU(Component):
    def __init__(self, *args, repo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._repo = repo if repo is not None else SolarRepository()
        self._parser = build_parser()
        self._tokenize = build_tokenize(self._repo)
        self._match_token = re.compile(r'<\w+>')
        self._act_regex = re.compile(r'^([\w_]+)\(([^\)]*)\)$')

    def _evaluate(self, x, logger):
        x = simplify(x)
        logger.info('NLU: simplified: "%s"' % x)
        x, tokens = self._tokenize(x)
        logger.info('NLU: tokenized: "%s"' % x)
        x = self._parser(x)
        if x is None:
            return []  # No result
        match = self._act_regex.match(x)
        if len(match.group(2).strip()) == 0:
            return [(match.group(1), None, None)]  # Intent only

        results = []
        tokens = deque(tokens)
        for slotvalue in match.group(2).split(','):
            slot, value = slotvalue.split(
                '=') if '=' in slotvalue else (slotvalue, None)

            # Map tokens back
            slot = self._match_token.sub(lambda _: tokens.popleft(), slot)
            if value is not None:
                value = self._match_token.sub(
                    lambda _: tokens.popleft(), value)

            results.append((match.group(1), slot, value))
        return results

    def __call__(self, dial, logger):
        result = self._evaluate(dial['user'], logger)
        dial['nlu'] = DA(list(starmap(DAI, result)))
        return dial
