import logging
from time import sleep

import psycopg
from psycopg.rows import scalar_row

CONN_PARAMS="host=postgres user=postgres password=secret dbname=scheduling"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

class Scheduler:
    def __init__(self, conn_params: str, broadcasting_interval: int=1):
        self.broadcasting_interval = broadcasting_interval
        self.notifier = psycopg.connect(conn_params, autocommit=True)

    def run(self):

        while True:

            with self.notifier.cursor(row_factory=scalar_row) as cursor:
                remaining_tasks = (
                    cursor
                    .execute(
                        "SELECT task.id FROM task WHERE task.state = 'pending' ORDER BY task.created_at ASC LIMIT 10",
                    )
                    .fetchall()
                )

                n_remaining_tasks = len(remaining_tasks)
                if n_remaining_tasks == 0:
                    logger.info("There are no remaining tasks in pending state")
                    break

                logger.info(f"Broadcasting {n_remaining_tasks} tasks")

                for task_id in remaining_tasks:
                    message = f"NOTIFY task_channel, '{task_id}';"
                    cursor.execute(message)

            sleep(self.broadcasting_interval)

        self.notifier.execute("NOTIFY task_channel, 'stop';")
        self.notifier.close()
        logger.info("Scheduler successfuly completed")


def create_tasks(conn_params: str):
    conn = psycopg.connect(conn_params, autocommit=True)
    for i in range(10):
        with conn.cursor() as cursor:
            result = (
                cursor
                .execute(f"INSERT INTO task(message) VALUES ('test-{i}') RETURNING id;")
                .fetchone()
            )
        if result is None:
            raise RuntimeError("Database returned invalid result on inserting task")
        if len(result) < 1:
            raise RuntimeError("Database returned invalid result on inserting task")
    conn.close()
    logger.info("Created tasks successfully")


def main():
    create_tasks(CONN_PARAMS)

    scheduler = Scheduler(CONN_PARAMS)
    scheduler.run()

if __name__ == "__main__":
    main()
