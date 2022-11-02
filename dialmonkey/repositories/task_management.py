import requests
from scipy.special import ellipe
from todoist.api import TodoistAPI
import scipy.constants
import re


'''
    TaskManagementRepository establish connection between Todoist API 
    and our Dialog System. The responses from the API are passed to dialog
    policy so that it can use its results to construct dialog actions.
'''


class TaskManagementRepository:

    def __init__(self):
        self.api = TodoistAPI("a5ce3e6fc7a0f999478b733608e3cee31754633f")
        self.api.sync()

    def _find_task(self, name, time=None, place=None):
        self.api.sync()
        for item in self.api.state["items"]:
            if name in item.data["content"]:
                return item
        return None

    def create_task(self, task):
        kwargs = {}
        for key in task.state_values:
            if key == "time":
                kwargs['due'] = {"string": task.state_values[key]}

        item = self.api.items.add(task.state_values["name"], **kwargs)
        result = None
        try:
            self.api.commit()
            result = item
        except Exception as e:
            print(e.message)
            result = "API_EXCEPTION"

        return result

    def get_task(self, task):
        kwargs = {}
        result = None
        try:
            result = self._find_task(task.state_values["name"])
        except Exception as e:
            print(e.message)
            result = "API_EXCEPTION"

        return result

    def get_tasks(self, task):
        kwargs = {}
        self.api.sync()
        items = []
        for item in self.api.state["items"]:
            if "time" in task.state_values.keys() and \
                    item.data["due"] is not None and \
                    task.state_values["time"] in item.data["due"]["string"]:
                items.append(item)

            elif "name" in task.state_values.keys() and \
                    item.data["content"] is not None and \
                    task.state_values["name"] in item.data["content"]:
                items.append(item)

        return items

    def delete_task(self, task):
        result = None
        try:
            item = self._find_task(task.state_values["name"])
            if item is None:
                return None
            item.delete()
            self.api.commit()
            result = item
        except Exception as e:
            print(e.message)
            result = "API_EXCEPTION"

        return result
