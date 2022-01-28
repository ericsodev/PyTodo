from __future__ import print_function, unicode_literals, annotations

from pprint import pprint
from typing import List, Dict, Callable

from PyInquirer import prompt, Separator, style_from_dict, Token
from models import Todo
from datetime import date, timedelta, datetime
import utilities as util
import os


class Interface:
    style: dict
    todos: List[Todo]
    categories: List[str]
    quit: bool

    def __init__(self):
        self.todos = util.get_tasks()
        self.categories = []
        self.update_categories()
        self.quit = False
        self.style = style = style_from_dict({
            Token.Separator: 'bg:#cc5454',
            Token.QuestionMark: '#673ab7',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: 'underline bold',
        })

    def _list_change_completion(self, original: Dict[str, Todo],
                                selected: List[str], confirm: bool) -> None:
        original_selected = 0
        num_selected = 0
        for name, task in original.items():
            if task.completed:
                original_selected += 1
            if name in selected:
                num_selected += 1
            task.completed = False

        if original_selected != num_selected:
            if confirm:
                ans = prompt([{"type": "confirm",
                         "name": "save",
                         "message": "Save changes?",
                         "default": True
                         }], style=self.style, qmark=">", vi_mode=True)
                if not ans:
                    return
            for name in selected:
                original[name].completed = True

    def _list_change_remove(self, original: Dict[str, Todo],
                            selected: List[str], confirm: bool) -> None:
        if len(selected) == 0:
            return
        if confirm:
            ans = prompt([{"type": "confirm",
                           "name": "save",
                           "message": "Save changes?",
                           "default": False
                           }], style=self.style, qmark=">", vi_mode=True)
            if not ans:
                return
        removals = []
        for name, task in original.items():
            task.completed = False
            if name in selected:
                removals.append(original[name])
        for task in removals:
            self.todos.remove(task)

    def update_categories(self):
        self.categories = []
        for task in self.todos:
            self.categories = list(
                set(self.categories).union(set(task.category)))

    def cmd_show(self, todos: List[Todo], fn: Callable,
                 auto_check_complete=True,
                 confirm=True, message: str="Tasks", long: bool=False):
        if len(todos) == 0:
            return
        util.filter_date(todos)
        task_dict = {}
        choices = []
        for task in todos:
            task_dict[task.__str__()] = task
            auto_check = task.completed if auto_check_complete else False
            choices.append(
                {
                    'name': task.__str__(long=long),
                    'checked': auto_check
                }
            )

        question = [
            {
                "type": "checkbox",
                "name": "main",
                "message": message,
                'choices': choices
            }
        ]
        ans = prompt(question, style=self.style, qmark=">", vi_mode=True)
        fn(task_dict, ans['main'], confirm=confirm)

    def cmd_today(self):
        self.cmd_show(util.filter_date(self.todos, 0),
                      self._list_change_completion,
                      message="Today's Tasks", long=True)

    def cmd_three_day(self):
        self.cmd_show(util.filter_date(self.todos, 2),
                      self._list_change_completion, message="3-Day Tasks")

    def cmd_read_only(self):
        self.cmd_show(self.todos, lambda a, b, confirm: None, confirm=False,
                      message="All Tasks (Read Only)")

    def cmd_filter(self):
        ans = prompt([
            {
                'type': 'input',
                'name': 'date',
                'message': 'Provide a positive date range from today ('
                           'negatives imply any date)',
                'default': '0'
            },
            {
                'type': 'confirm',
                'name': 'past_dates',
                'message': 'Show tasks from the past?',
                'default': True
            },
            {
                'type': 'confirm',
                'name': 'completed',
                'message': "Show completed Todos?",
                'default': True
            },
            {
                'type': 'input',
                'name': 'category',
                'message': "Provide any categories you want to filter for",
                'default': ""
            },
        ], style=self.style, qmark=">", vi_mode=True)

        candidates = self.todos
        if ans['date'].isdigit() and int(ans['date']) >= 0:
            candidates = util.filter_date(candidates, int(ans['date']),
                                          future_only=ans['past_dates'])
        if not ans['completed']:
            candidates = util.filter_completion(candidates,
                                                completed=False)

        categories = [c.strip().lower() for c in ans['category'].split(',')]
        if categories[0] != '':
            q = prompt([
                {
                    'type': 'confirm',
                    'name': 'category_all',
                    'message': 'Only show Todos that match all categories?',
                    'default': False
                }
            ])
            candidates = util.filter_categories(candidates, categories,
                                                q['category_all'])

        self.cmd_show(candidates,
                      self._list_change_completion,
                      message="Here are your results:")

    def cmd_add(self):
        question = [
            {
                "type": "input",
                "name": "name",
                "message": "Task name:",
                "default": ""
            },
            {
                "type": "input",
                "name": "date",
                "message": "Date('dd mm yy', 'td', 'tmr'):",
                "default": ""
            },
            {
                "type": "input",
                "name": "cat",
                "message": "Categories (Comma separated):",
                "default": ""
            }
        ]
        ans = prompt(question)
        todo_date = None
        if ans['name'] == '':
            return

        if ans['date'] == 'td':
            todo_date = date.today()
        elif ans['date'] == 'tmr':
            todo_date = date.today() + timedelta(days=1)
        else:
            try:
                todo_date = datetime.strptime(ans['date'], '%d %m %y').date()
            except ValueError:
                return

        data = {'name': ans['name'], 'date': todo_date.isoformat(),
                'completed': False,
                'category': [c.strip().lower() for c in ans['cat'].split(',')]}
        self.todos.append(Todo(data))
        pprint(self.todos)

    def cmd_remove(self):
        self.cmd_show(self.todos, self._list_change_remove,
                      auto_check_complete=False, message="Remove Tasks")

    def cmd_save(self):
        ans = prompt([
            {
                'type': 'confirm',
                'name': 'main',
                'message': 'Save all changes made?',
                'default': True
            }
        ], style=self.style, qmark=">", vi_mode=True)
        if not ans['main']:
            return
        else:
            util.save_tasks(self.todos)

    def cmd_quit(self):
        self.cmd_save()
        self.quit = True
        print("==== Bye Bye ====")

    def cmd_base(self):
        commands = {'today': self.cmd_today, '3-day': self.cmd_three_day,
                    'filter': self.cmd_filter,
                    'read all': self.cmd_read_only, 'add': self.cmd_add,
                    'remove': self.cmd_remove,
                    'save': self.cmd_save, 'quit': self.cmd_quit}
        questions = [
            {
                "type": "list",
                "name": "main",
                "message": "What do you want to do?",
                "choices": [Separator('==== View ===='), 'Today', '3-day',
                            'Read All',
                            Separator('==== Manage ===='), 'Add', 'Remove',
                            'Filter',
                            Separator('==== Save / Quit ===='), 'Save', 'Quit'],
                "filter": lambda x: x.lower()
            }
        ]

        cmd = prompt(questions, style=self.style, vi_mode=True, qmark=">")
        commands.setdefault(cmd['main'], print)()

    def start(self):
        while not self.quit:
            self.cmd_base()
            os.system('cls' if os.name == 'nt' else 'clear')
