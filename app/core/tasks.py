import time

from celery import group
from celery.utils.log import get_task_logger

from app import celery, redis_client

logger = get_task_logger(__name__)

# no. of concurrent tasks that can be executed
TASK_CONCURRENCY_LIMIT = 1
# redis key to lock access to callback task
TASK_EXECUTOR_KEY = 'task_executor__in_progress'
# redis list containing all pending tasks to run
TASK_EXEC_LIST_KEY = 'task_executor__pending_list'


@celery.task(name='core.tasks.test',
             soft_time_limit=60, time_limit=65)
def test_task():
    logger.info('running test task')
    return True


@celery.task(name='core.tasks.queue_task_executor')
def queue_task_executor(**kwargs):
    logger.debug(f'queue_task_executor called with {kwargs}')
    request_id = kwargs.get('request_id')
    is_called_by_callback = kwargs.get('is_called_by_callback', False)
    if not is_called_by_callback:
        # push to queue
        logger.info(f'pushing id: {request_id} to queue')
        redis_client.rpush(TASK_EXEC_LIST_KEY, request_id)
        queue_task_executor_callback.apply_async(kwargs={})
        return
    # execute the task here
    time.sleep(5)
    logger.info(f'task id:{request_id} execution completed successfully!')


@celery.task(name='core.tasks.queue_task_executor_callback')
def queue_task_executor_callback(**kwargs):
    logger.debug(f'queue_task_executor_callback called {kwargs}')
    if kwargs and kwargs.get('pick_next'):  # only delete this key if called via completing tasks
        redis_client.delete(TASK_EXECUTOR_KEY)
    if redis_client.setnx(TASK_EXECUTOR_KEY, 1):
        # retrieve first x elements from the queue
        next_tasks = redis_client.lrange(TASK_EXEC_LIST_KEY, 0, TASK_CONCURRENCY_LIMIT - 1)
        tasks = []
        if len(next_tasks):
            tasks = [
                queue_task_executor.signature(
                    kwargs={
                        'request_id': int(val),
                        'is_called_by_callback': True
                    }
                )
                for val in next_tasks
            ]
            # delete x elements from queue
            redis_client.ltrim(TASK_EXEC_LIST_KEY, TASK_CONCURRENCY_LIMIT, -1)
            job = group(tasks)
            job.link(queue_task_executor_callback.signature(kwargs={'pick_next': True}))
            _ = job.apply_async()
        else:
            # this means this was the last callback
            redis_client.delete(TASK_EXECUTOR_KEY)
    else:
        logger.debug(f'queue_task_executor_callback already in progress {redis_client.get(TASK_EXECUTOR_KEY)}')
