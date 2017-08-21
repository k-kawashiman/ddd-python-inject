# -*- coding: utf-8 -*-
u""" CLI インタフェース """
import logging

import click
import inject

from .config import create_config
from .read_model.updater import register_readmodel_updater
from todolist.domain_model.task import Task, TaskStatus, TaskRepository
from todolist.domain_model.user import UserService
from todolist.read_model.task import TaskQuery


logging.basicConfig(level=logging.INFO)


@click.group()
def main():
    params = {
        "redis_host": "localhost",
        "redis_port": "6379",
        "redis_db": "2",
    }
    inject.configure(create_config(params))
    register_readmodel_updater()


@main.command()
def list():
    query = inject.instance(TaskQuery)
    user = inject.instance(UserService).get_current_user()
    tasks = query.find_by_user_id(user.user_id)
    for task in tasks:
        if task.status is TaskStatus.todo:
            click.echo(u"[ ] #{}: {}".format(task.task_id, task.name))
        else:
            click.echo(u"[x] #{}: {}".format(task.task_id, task.name))


@main.command()
@click.option("--name", type=unicode, help="task name", prompt="task name")
def add(name):
    repo = inject.instance(TaskRepository)
    user = inject.instance(UserService).get_current_user()
    task = Task.create(user.user_id, name)
    repo.save(task)
    click.echo(u"#{}: {}".format(task.task_id, task.name))


@main.command()
@click.argument("task_id", type=int)
def done(task_id):
    repo = inject.instance(TaskRepository)
    user = inject.instance(UserService).get_current_user()
    task = repo.get(user.user_id, task_id)
    if task is None:
        click.echo("task not found: #{}".format(task_id))
    elif task.status is TaskStatus.todo:
        task.done()
        repo.save(task)
    click.echo(u"[x] #{}: {}".format(task.task_id, task.name))
