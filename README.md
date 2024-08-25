# Worker / Scheduler POC

This project is an experiment at using Postgres as a message queue. Postgres holds the details of the tasks - that are inserted at the start of scheduling for simplicity - and it's notification capabilities are used to let the workers know that there are tasks that have not been completed.

The upside of this approach is that workers do not need to query the database for unfinished tasks, instead they are notified when `pending` work is in the queue. All workers receive the broadcast too, even if they are busy `processing`. The fastest worker picks up the new task and puts a row lock on it to avoid having two processing the same task twice. Once a task is done it is `completed`.

The scheduler periodically fetches the `pending` tasks and broadcasts their ids to the workers. Once all tasks have been completed the scheduler will send the special `stop` message to stop all workers.