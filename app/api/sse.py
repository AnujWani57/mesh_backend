import asyncio
from typing import List

SOS_SUBSCRIBERS: List[asyncio.Queue] = []


def notify_sos_event(alert_payload: dict):
    for queue in list(SOS_SUBSCRIBERS):
        try:
            queue.put_nowait(alert_payload)
        except asyncio.QueueFull:
            continue


def register_sos_subscriber(queue: asyncio.Queue):
    SOS_SUBSCRIBERS.append(queue)


def unregister_sos_subscriber(queue: asyncio.Queue):
    if queue in SOS_SUBSCRIBERS:
        SOS_SUBSCRIBERS.remove(queue)
