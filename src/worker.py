import logging
import random
from time import sleep

import psycopg
from psycopg.errors import LockNotAvailable
from psycopg.rows import class_row
from psycopg.types.enum import EnumInfo, register_enum

from entitites import Task, TaskState

GET_TASK_DATA="SELECT * FROM task WHERE id = %(id)s AND state = 'pending' FOR UPDATE NOWAIT;"
UPDATE_TASK_STATE="UPDATE task SET state = %(task_state)s WHERE id = %(id)s;"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

class Worker:
    def __init__(self, conn_params: str):
        self.listener = psycopg.connect(conn_params, autocommit=True)

        self.retriever = psycopg.connect(
            conn_params,
            row_factory=class_row(Task),
            autocommit=True
        )
        info = EnumInfo.fetch(self.retriever, "task_state")
        if info is None:
            raise RuntimeError("Could not fetch enum `task_state`")
        register_enum(info, self.retriever, TaskState)

    def run(self):
        self.listener.execute("LISTEN task_channel;")

        for notification in self.listener.notifies():
            payload = notification.payload
            if payload == "stop":
                self.listener.close()
                self.retriever.close()
                break
            try:
                task_id = int(payload)
                self.process_task(task_id)
            except ValueError:
                logger.error(f"Could not parse task id from payload: {payload}")
                continue

    def process_task(self, task_id: int):
        with self.retriever.cursor() as cursor:
            try:
                task: Task = (
                    cursor
                    .execute(GET_TASK_DATA, params={"id": task_id})
                    .fetchone()
                )
                if task.state in (TaskState.processing, TaskState.completed):
                    return
            except LockNotAvailable:
                logger.debug(f"Skipping locked task {task_id}")
                return

            if task is None:
                return

            logger.info(f"Processing task {task.id}")
            cursor.execute(UPDATE_TASK_STATE, params={"task_state": TaskState.processing, "id": task.id})

            processing_time = random.randint(0, 10)
            sleep(processing_time)

            cursor.execute(UPDATE_TASK_STATE, params={"task_state": TaskState.completed, "id": task.id})
            logger.debug(f"Finished task {task_id}")


def main():
    worker = Worker("host=postgres user=postgres password=secret dbname=scheduling")
    worker.run()

if __name__ == "__main__":
    main()
