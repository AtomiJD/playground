import concurrent.futures
import os
import time
import random
from jdtasks import *

class RunTask:
    def __init__(self, task: Task):
        self.task = task

    def run(self):
        print(f"Task: {self.task.description}, Progress: {self.task.progress}")
        for cmd in self.task.cmdlist:
            print(f"{cmd['command']}")        
        time.sleep(1)
        return self.task.description

def my_function(task: Task):
    try:
        print(f"Processing {task.number} in process ID {os.getpid()}")
        l = RunTask(task)
        return l.run()

    except Exception as e:
        print(f"An error occurred in the worker process: {e}")
        return None

def main():
    data = []
    loaded_tasks = load_tasks_from_json('_tasks.json')
    for task in loaded_tasks:
        for subtask in task.iter_tasks():
            if subtask.progress < 100:
                data.append(subtask)
    while True:
        if data:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(executor.map(my_function, data))
            print("Results:", results)
            for d in data:
                if d.progress > 100:
                    data.remove(d)
                else:
                    d.progress += random.randint(1,25)                    
        else:
            break

if __name__ == '__main__':
    main()
