from __future__ import annotations

from typing import List, Dict, Any, Union
from datetime import date


class Todo:
    """ A class representing a task

    """
    date: Union[date, None]
    name: str
    category = List[str]
    completed: bool
    hidden: bool

    def __init__(self, data: dict) -> None:
        self.name = data['name']
        self.completed = data.setdefault('completed', False)
        self.hidden = False
        if data['date'] == '':
            self.date = None
        else:
            self.date = date.fromisoformat(data['date'])

        self.category = []
        for cat in data['category']:
            self.category.append(cat)

    def __str__(self, long=False) -> str:
        if not self.date:
            return f'{self.name}]'
        else:
            if long:
                return f'{self.name} - {self.date.strftime("%b %d (%a)")}'
            else:
                return f'{self.name} - {self.date.strftime("%b %d (%a)")}'

    def get_dict(self) -> Dict[str, Any]:
        data = {'name': self.name, 'completed': self.completed, 'category': self.category, 'date': ''}
        if self.date:
            data['date'] = self.date.isoformat()
        return data
