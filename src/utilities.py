from __future__ import print_function, unicode_literals
from typing import List, Dict, Any
from datetime import timedelta, date
import json
from models import Todo


# Load JSON Data
def get_tasks(path="data.json") -> List[Todo]:
    raw_data = ""
    with open(path) as file:
        raw_data = file.read()

    data = json.loads(raw_data)
    if 'tasks' not in data:
        return []
    return [Todo(todo) for todo in data['tasks']]


# Write JSON Data
def save_tasks(tasks: List[Todo], path="data.json") -> None:
    data = get_dict(tasks)
    with open(path, 'w') as file:
        json.dump(data, file, indent=2)


# Convert data to dict
def get_dict(tasks: List[Todo]) -> Dict[str, Dict[str, Any]]:
    data = {}
    for task in tasks:
        data.setdefault('tasks', []).append(task.get_dict())

    return data


def filter_date(tasks: List[Todo], date_range: int = 0, future_only: bool = True) -> List[Todo]:
    """ Returns a list of Todos within the given date range

    :param tasks: The list of tasks to filter
    :param date_range: The date delta that Todos must be within
    :param future_only: Whether the date range should include past dates
    """
    candidates = []
    if not tasks:
        return []
    for task in tasks:
        margin = timedelta(days=date_range)
        if future_only:
            if date.today() <= task.date <= date.today() + margin:
                candidates.append(task)
        else:
            if date.today() - margin <= task.date <= date.today() + margin:
                candidates.append(task)
    return candidates


def filter_categories(tasks: List[Todo], categories: List[str], match_all: bool = True) -> List[Todo]:
    """ Returns a list of Todos that includes the given categories

    :param tasks: The list of tasks to filter
    :param categories: The list of categories the Todos must include
    :param match_all: Whether the Todos must include all categories or at least one
    """
    if not tasks:
        return []
    candidates = []
    for task in tasks:
        if match_all:
            if set(categories).issubset(set(task.category)):
                candidates.append(task)
        else:
            if set(task.category).intersection(set(categories)):
                candidates.append(task)
    return candidates


def filter_completion(tasks: List[Todo], completed: bool = True) -> List[Todo]:
    """ Returns a list of Todos that fulfills the completion requirement

    :param tasks: The full list of Todos to filter
    :param completed: Whether the Todos are completed
    """
    if not tasks:
        return []
    candidates = []
    for task in tasks:
        if task.completed == completed:
            candidates.append(task)
    return candidates
