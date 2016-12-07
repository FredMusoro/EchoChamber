"""
Test client connections to a XMPP chat room
"""
import math
import time
import bisect
import logging
import random

import pytest

from echochamber.utils import create_client_connections, establish_channel


@pytest.mark.parametrize("num_clients", [
    10,
])
def test_messaging(client_factory, debug, num_clients):
    """
    Test that clients connect and can send varying number of messages
    """
    total_time = 200  # Time period for sending all messages
    frequency_high = 0.60  # 6 messages every 10 seconds
    frequency_low = 0.10  # 1 message every 10 seconds
    # threshhold = 300
    percentage_high_users = 0.1

    # Join all clients to the room
    clients = create_client_connections(client_factory, num_clients)
    establish_channel(clients)
    logging.info("All clients have been invited to the channel, sending message tests")

    num_high_users = int(math.ceil(num_clients * percentage_high_users))
    high_users, low_users = clients[0:num_high_users], clients[num_high_users:]

    logging.info("Chose %d high frequency messaging users and %d low frequency users.",
                 len(high_users), len(low_users))

    message_queue = []
    for client in clients:
        if client in high_users:
            msg_freq = frequency_high
        else:
            msg_freq = frequency_low
        num_messages = int(total_time * msg_freq)

        # Schedule each message to be sent by this client
        for i in range(num_messages):
            # Pick a random time in the total_time range to send the message
            # bisect.insort will queue messages in the list ordered by scheduled time
            queued_time = random.uniform(0, total_time)
            bisect.insort_right(message_queue, (queued_time, client))

    # Run a loop and send all queued messages at the schedule times
    start_time = time.time()
    message_id = 0
    total_messages = len(message_queue)

    while message_queue:
        # Check if first message is ready to be sent (we have reached the scheduled send time)
        if (time.time() - start_time) > message_queue[0][0]:
            queued_time, client = message_queue.pop(0)
            message_id += 1
            logging.info("Sending message %d for %s queued at %0.2f",
                         message_id, client.username, queued_time)

            client.send_message("{message_id} {time:0.2f} {username}".format(
                message_id=message_id,
                time=queued_time,
                username=client.username)
            )

    logging.info("Finished sending %d messages", total_messages)

    # Wait for all messages to be received be each jabberite client
    time.sleep(5)

    for client in clients:
        # Check that each client received all the messages
        assert len(client.get_all_messages()) == total_messages

    logging.info("All clients received all sent messages")
