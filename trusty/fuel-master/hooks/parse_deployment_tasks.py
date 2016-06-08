#!/usr/bin/python

import argparse
import random
import os
import yaml


FIRST_STAGE = 2000
STAGE_STEP  = 10


class TaskProcessor:
    def __init__(self, deployment_tasks):
        self.__deployment_tasks = deployment_tasks
        self.__tasks = []
        self.__in_progress_tasks = set()

    @property
    def tasks(self):
        self.__process()
        tasks_list = []
        stage = FIRST_STAGE
        for t in self.__tasks:
            task_obj = self.__get_task(t)
            file = task_obj['parameters']['puppet_manifest'].split('/')[-1]
            roles = ','.join(task_obj['role'])
            tasks_list.append('%s:%s:%s' % (stage, roles, file))
            stage += STAGE_STEP
        return tasks_list

    @property
    def stages(self):
        return [i.split(':')[0] for i in self.tasks]

    def __process(self):
        for task in self.__deployment_tasks:
            self.__process_task(task)
    
    def __process_task(self, task):
        name = task['id']
        if name == 'scaleio-environment-check':
            return
        if name in self.__tasks:
            return
        if name in self.__in_progress_tasks:
            raise Exception(
                "Broken deployment tasks structure."
                " There is cycle in dependencies: name=%s, "
                " stack of tasks=%s" % (name, self.__in_progress_tasks))
        self.__in_progress_tasks.add(name)
        index = 0
        # process tasks which this task depends from
        for parent in task['requires']:
            if parent == 'post_deployment_start':
                continue
            i = None
            try:
                i = self.__tasks.index(parent)
            except ValueError:
                # TODO: check for cycles
                self.__process_task(self.__get_task(parent))
                i = self.__tasks.index(parent)
            if i >= index:
                index = i + 1
        # process tasks which depend from this task
        for parent in task['required_for']:
            if parent == 'post_deployment_end':
                continue
            raise Exception("TODO: impl me") # TODO: impl if needed
        self.__tasks.insert(index, name)
        self.__in_progress_tasks.remove(name)

    def __get_task(self, name):
        for t in self.__deployment_tasks:
            if t['id'] == name:
                return t
        raise Exception(
            "Broken deployment tasks structure."
            " There is reference to non-existing tasks %s" % name)

    
def main(args):
    with open(args.file, 'r') as stream:
        parsed_tasks = yaml.load(stream)
        if args.test:
            random.shuffle(parsed_tasks)        
        tp = TaskProcessor(parsed_tasks)
        if args.tasks:
            for t in tp.tasks:
                print(t)
        elif args.stages:
            for t in tp.stages:
                print(t)
                

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--file', dest='file', type=str, default='deployment_tasks.yaml')
  parser.add_argument('--test', dest='test', action='store_true') # does shuffle of tasks to test algorithm
  parser.add_argument('--stages', dest='stages', action='store_true')
  parser.add_argument('--tasks', dest='tasks', action='store_true')

  main(parser.parse_args())

