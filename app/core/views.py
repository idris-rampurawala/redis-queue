
from flask import Blueprint, current_app, request
from werkzeug.local import LocalProxy

from authentication import require_appkey

from .tasks import queue_task_executor, test_task

core = Blueprint('core', __name__)
logger = LocalProxy(lambda: current_app.logger)


@core.before_request
def before_request_func():
    current_app.logger.name = 'core'


@core.route('/test', methods=['GET'])
def test():
    logger.info('app test route hit')
    test_task.delay()
    return 'Congratulations! Your core-app test route is running!'


@core.route('/requestor', methods=['POST'])
def requestor():
    request_data = request.json
    logger.info(f'requesttor {request_data}')
    queue_task_executor.apply_async(kwargs={'request_id': request_data.get('id')})
    return 'Added to queue'


@core.route('/restricted', methods=['GET'])
@require_appkey
def restricted():
    return 'Congratulations! Your core-app restricted route is running via your API key!'
