import json
from datetime import datetime

class Cmd:
    def __init__(self, command, *args):
        self.command = command
        self.args = args

    def __repr__(self):
        return f"Cmd(command={self.command}, args={self.args})"
    
    def to_dict(self):
        return {
            'command': self.command,
            'args': self.args
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['command'], *data['args'])

class Task:
    def __init__(self, number, priority, description, start_date, end_date, progress=0):
        self.number = number
        self.priority = priority
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.progress = progress
        self.subtasks = []
        self.cmdlist = []
        self.next = None
        self.previous = None

    def add_subtask(self, subtask):
        if self.subtasks:
            last_subtask = self.subtasks[-1]
            last_subtask.next = subtask
            subtask.previous = last_subtask
        self.subtasks.append(subtask)

    def add_cmd(self, cmd):
        self.cmdlist.append(cmd)

    def iter_tasks(self):
        yield self
        for subtask in self.subtasks:
            yield from subtask.iter_tasks()        

    def to_dict(self):
        task_dict = {
            'number': self.number,
            'priority': self.priority,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'progress': self.progress,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks],
            'cmdlist': [cmd.to_dict() for cmd in self.cmdlist],
        }
        return task_dict

    @classmethod
    def from_dict(cls, task_dict):
        task = cls(
            task_dict['number'],
            task_dict['priority'],
            task_dict['description'],
            task_dict['start_date'],
            task_dict['end_date'],
            task_dict['progress']
        )
        for subtask_dict in task_dict['subtasks']:
            subtask = cls.from_dict(subtask_dict)
            task.add_subtask(subtask)
        for cmd_dict in task_dict['cmdlist']:
            #cmd:Cmd = cmd_dict.from_dict(cmd_dict)
            task.add_cmd(cmd_dict)
        return task

def save_tasks_to_json(tasks, filename):
    tasks_list = [task.to_dict() for task in tasks]
    with open(filename, 'w') as f:
        json.dump(tasks_list, f)

def load_tasks_from_json(filename):
    with open(filename, 'r') as f:
        tasks_list = json.load(f)
    return [Task.from_dict(task_dict) for task_dict in tasks_list]

def display_tasks(tasks, level=0):
    for task in tasks:
        print("  " * level + f"{task.description}")
        for cmd in task.cmdlist:
            print("  " * level + f"{cmd['command']}")
        display_tasks(task.subtasks, level+1)

if __name__ == "__main__":
    task1 = Task(1, 1, "Task 1", "2023-04-01", "2023-04-30", 0)
    task2 = Task(2, 2, "Task 2", "2023-05-01", "2023-05-30", 0)

    task1_subtask1 = Task(1, 1, "Task 1 Subtask 1", "2023-04-01", "2023-04-15", 0)
    task1.add_subtask(task1_subtask1)

    task1_subtask2 = Task(2, 2, "Task 1 Subtask 2", "2023-04-15", "2023-04-30", 0)
    task1.add_subtask(task1_subtask2)

    subtask1_subtask1 = Task(1, 1, "Task 1 Subtask 1 Subtask 1", "2023-04-01", "2023-04-15", 0)
    task1_subtask1.add_subtask(subtask1_subtask1)
    cmd = Cmd("cls")
    task1_subtask1.add_cmd(cmd)
    cmd = Cmd("load", "lall.json")
    task1_subtask1.add_cmd(cmd)    
    cmd = Cmd("run", "lall")
    task1_subtask1.add_cmd(cmd)

    subtask1_subtask2 = Task(2, 2, "Task 1 Subtask 1 Subtask 2", "2023-04-15", "2023-04-30", 0)
    task1_subtask1.add_subtask(subtask1_subtask2)

    tasks = [task1, task2]
    save_tasks_to_json(tasks, '_tasks.json')

    loaded_tasks = load_tasks_from_json('_tasks.json')

    # Display the loaded tasks and their subtasks
    print("Loaded tasks and their subtasks:")
    display_tasks(loaded_tasks)

    print("All tasks and subtasks using iterator:")
    for task in loaded_tasks:
        for subtask in task.iter_tasks():
            print(subtask.description)
