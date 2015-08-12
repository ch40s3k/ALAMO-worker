'''Example rabbitmq publisher - simulation of ALAMO-scheduler.
It generates 2k checks in 1 sec intervals.
'''

import asyncio
import asynqp
import json

QUERY = {
  "metrics": [
    {
      "tags": {},
      "name": "kairosdb.datastore.cassandra.key_query_time",
      "group_by": [
        {
          "name": "tag",
          "tags": [
            "query_index"
          ]
        }
      ],
      "aggregators": [
        {
          "name": "sum",
          "align_sampling": True,
          "sampling": {
            "value": "1",
            "unit": "seconds"
          }
        }
      ]
    }
  ],
  "cache_time": 0,
  "start_relative": {
    "value": "1",
    "unit": "hours"
  }
}





MESSAGE = {
    'name': 'test',
    'interval': '60',
    'type': 'kairosdb',
    'query': json.dumps(QUERY),
    'debounce': 5,
    'tags': {'key': 'value'},
    'treshold_value': 10,
    'operator': 'AND',
    'severity': 'HIGH',
    'integration_key': 123456789,
    'last_run': 123456789
}


@asyncio.coroutine
def setup_connetion(loop):
    # Connecting to broker.
    connection = yield from asynqp.connect('localhost', 5672)

    return connection


@asyncio.coroutine
def setup_exchange_and_queue(connection):

    # Open a communication channel
    channel =  yield from connection.open_channel()

    # Create a queue and exchange on the broker
    exchange = yield from channel.declare_exchange('scheduled.task', 'direct')
    queue = yield from channel.declare_queue('queue.tasks')

    # Bind the queue to exchange
    yield from queue.bind(exchange, 'routing_key')

    return exchange, queue


@asyncio.coroutine
def setup_producer(connection):

    exchange, _ = yield from setup_exchange_and_queue(connection)

    while True:
        count = 0
        while count != 2000:
            check = 'Check_{}'.format(count)
            msg = asynqp.Message({check: MESSAGE})
            exchange.publish(msg, 'routing_key')
            count += 1
        yield from asyncio.sleep(1)


@asyncio.coroutine
def start(loop):
    try:
        connection = yield from setup_connetion(loop)
        producer = asyncio.Task(setup_producer(connection))

    except Exception:
        print('failed to connect, trying again')
        yield from asyncio.sleep(1)
        asyncio.Task(start(loop))


def main():

    loop = asyncio.get_event_loop()
    asyncio.Task(start(loop))
    loop.run_forever()

if __name__ == "__main__":
    main()