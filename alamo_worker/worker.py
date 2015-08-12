import asyncio
import asynqp


@asyncio.coroutine
def setup_connetion(loop):
    # Connecting to broker.

    connection = yield from asynqp.connect('localhost', 5672)

    return connection


@asyncio.coroutine
def setup_exchange_and_queue(connection):

    channel = yield from connection.open_channel()
    channel.set_qos(prefetch_count=1)
    exchange = yield from channel.declare_exchange('scheduled.task', 'direct')
    queue = yield from channel.declare_queue('queue.tasks')

    return exchange, queue


@asyncio.coroutine
def setup_consumer(connection):

    def callback(msg):
        print('Received: {}'.format(msg.json()))
        msg.ack()

    _, queue = yield from setup_exchange_and_queue(connection)
    consumer = yield from queue.consume(callback)
    return consumer


@asyncio.coroutine
def start(loop):
    try:
        connection = yield from setup_connetion(loop)
        consumer = asyncio.Task(setup_consumer(connection))

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