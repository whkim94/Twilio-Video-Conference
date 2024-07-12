from .models import Room
from schedule.models import Reservation
from config.celery import app
from datetime import datetime, timedelta
import random
import string
from django.db import transaction
from django.utils import timezone


def new_room(mentor, questioner):
    allowed_chars = ''.join((string.ascii_letters, string.digits))
    new_room = None
    while not new_room:
        with transaction.atomic():
            group_name = 'chat-'
            group_name += ''.join(random.choice(allowed_chars) for _ in range(32))
            if Room.objects.filter(group_name=group_name).exists():
                continue
            new_room = Room.objects.create(mentor=mentor, questioner=questioner, group_name=group_name)
    return new_room


@app.task
def allocate_chat_room():
    # Bring Reservations that are within 10 minutes
    reservations = Reservation.objects.filter(expired=False,
                                              r_type=1,
                                              room__isnull=True,
                                              start_time__range=[timezone.now() - timedelta(seconds=5),
                                                                 timezone.now() + timedelta(minutes=10)])

    if reservations.exists():
        for r in reservations:
            room = new_room(r.mentor, r.booker)
            r.assign_room(room)
            r.save()
        return "Assigned Chat Link. = {}".format(datetime.now()) # 서울시간 보여주기

    return "There is no Chat Room."


@app.task
def enable_chat():
    # Enable Chat before 1 minute of conference
    reservations = Reservation.objects.filter(expired=False,
                                              r_type=1,
                                              room__isnull=False,
                                              start_time__range=[timezone.now() - timedelta(seconds=5),
                                                                 timezone.now() + timedelta(minutes=1)]).select_related('room')

    if reservations.exists():
        for r in reservations:
            room = r.room
            room.enable_chat()
            room.save()

        return "Assigned Chat Link To Reservation. = {}".format(datetime.now())

    return "There is no reservation to chat."
