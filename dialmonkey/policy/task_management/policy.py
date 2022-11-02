from ...component import Component
from ...utils import choose_one
from itertools import groupby
from dialmonkey.da import DA, DAI
from dialmonkey.dialogue import Dialogue
from dialmonkey.utils import choose_one
from inspect import signature
from dialmonkey.repositories import TaskManagementRepository


class RequestQueryMapper:
    def __init__(self, repo):
        self._repo: TaskManagementRepository = repo

    def _validate_response(self, response):
        if response is None:
            return [("error", "task", "not_found")]
        elif response == "API_EXCEPTION":
            return [("error", "api_exception")]
        return True

    def greet(self):
        return ('greet', None, None)

    def request_more(self):
        return ("request_more", None, None)

    def goodbye(self, thanks=None):
        return ('exit', None, None)

    def create_task(self, context):

        if "name" not in context.state_values:
            return [("more_info", "name", None)]

        response = self._repo.create_task(context)
        item = response.data
        result = []
        result.append(
            ("task_created", "name", item["content"]))

        if item["due"] is not None:
            result.append(
                ("task_created", "time", item["due"]["string"]))

        return result

    def get_task(self, context):
        response = self._repo.get_task(context)

        if response is None:
            return [("error", "task", "not_found")]
        elif response == "API_EXCEPTION":
            return [("error", "api_exception")]

        result = []

        item = response.data

        result.append(("task_info", "name", item["content"]))
        result.append(("task_info", "date_added", item["date_added"]))
        if item["due"] is not None:
            result.append(("task_info", "time", item["due"]["string"]))

        return result

    def get_tasks(self, context):
        result = self._repo.get_tasks(context)

        if len(result) == 0:
            return [("error", "tasks", "not_found")]

        task_list = ""
        for i in range(len(result)):
            if i > 0:
                task_list += ","
            item_string = "name=" + result[i].data["content"]
            if "time" not in context.state_values and result[i].data["due"] is not None:
                item_string += "|" + "time=" + result[i].data["due"]["string"]

            task_list += item_string

        dais = []

        if "time" in context.state_values:
            dais.append(("tasks_info", "time", context.state_values["time"]))
        dais.append(("tasks_info", "list", task_list))

        return dais

    def delete_task(self, context):
        response = self._repo.delete_task(context)

        if response is None:
            return [("error", "task", "not_found")]
        elif response == "API_EXCEPTION":
            return [("error", "api_exception")]

        result = []
        result.append(
            ("task_deleted", "name", response.data["content"]))

        return result

    def __call__(self, intent, values, state_values):
        if not hasattr(self, intent):
            return None
        method = getattr(self, intent)
        try:
            parameters = signature(method).parameters
            required = [x for x, y in parameters.items()
                        if y.default is not None]
            for r in required:
                if r == 'context':
                    continue
                if r not in values:
                    raise RequiredSlot(r)
            nargs = {k: v for k, v in values.items() if k in parameters}
            if 'context' in parameters:
                nargs['context'] = Context(intent, values, state_values)
            return method(**nargs)
        except DirectResponse as e:
            return e.value


class Context:
    def __init__(self, intent, values, state_values):
        self.intent = intent
        self.values = values
        self.state_values = state_values
        self.state_change = lambda state: state

    def require(self, slot, allow_state=True):
        if slot in self.values:
            return self.values[slot]
        if allow_state and slot in self.state_values:
            return self.state_values[slot]
        raise RequiredSlot(slot)

    def try_get(self, slot, default=None, allow_state=True):
        if slot in self.values:
            return self.values[slot]
        if allow_state and slot in self.state_values:
            return self.state_values[slot]
        return default

    def push_state(slot, value):
        change = self.state_change

        def state_update(state):
            state = dict(**change(state))
            state.update({slot: {value: 1.0, None: 0.0}})
            return state
        self.state_change = state_update


class DirectResponse(BaseException):
    def __init__(self, value):
        self.value = value


class RequiredSlot(DirectResponse):
    def __init__(self, slot):
        super().__init__(('request', slot, None))


class TaskManagementPolicy(Component):

    def __init__(self, *args, repo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._threshold = 0.7
        self._repository = repo if repo is not None else TaskManagementRepository()
        self._mapper = RequestQueryMapper(self._repository)

    def _map_call(self, da: DA, state) -> DA:
        assert da is not None
        assert isinstance(da, DA)
        assert state is not None
        if not da.dais:
            return DA([DAI('error', 'not_understood', None)])

        dai = [(x.intent, x.confidence) for x in da.dais]
        dai.sort()
        dai = [(k, sum(map(lambda x: x[1], s)))
               for k, s in groupby(dai, key=lambda x: x[0])]
        dai.sort(reverse=True)

        # We support single intent for now
        intent, _ = dai[0]
        values = {x.slot: x.value for x in da.dais if x.confidence >
                  self._threshold}
        state_values = ((k, max((p if p is not None else 'none', v if v is not None else 'none')
                        for v, p in x.items())) for k, x in state.items() if k is not None and not k.startswith('_'))
        state_values = {
            k: v for k, (p, v) in state_values if p > self._threshold and isinstance(k, str)}

        # Add meta attributes
        state_values.update(
            **{k: x for k, x in state.items() if k is not None and k.startswith('_')})
        response = self._mapper(intent, values, state_values)
        if response is None:
            response = list()
        elif not isinstance(response, list):
            response = [response]

        # Map to DA
        da = DA()
        for r in response:
            da.append(DAI(*r))

        return da

    def __call__(self, dial: Dialogue, logger):
        response: DA = self._map_call(dial['nlu'], dial['state'])
        dial.action = response

        if any((x for x in response.dais if x.intent == 'exit')):
            dial.end_dialogue()
        return dial

    def reset(self):
        pass
