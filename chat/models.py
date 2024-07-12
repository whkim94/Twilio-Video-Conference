from __future__ import unicode_literals
from django.contrib.auth.models import User
from accounts.profile_model import MentorProfile
from django.db import models
from django.utils import timezone


class Room(models.Model):
    mentor = models.ForeignKey(MentorProfile, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Mentor')
    questioner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='User')

    group_name = models.SlugField(verbose_name='Room_Code', unique=True)

    create = models.DateTimeField('Created_Date', auto_now_add=True, db_index=True)
    enabled = models.BooleanField('Is_Room_Enables', default=False)

    expired = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name

    class Meta:
        ordering = ['-id', 'mentor', 'create', ]
        verbose_name = "Chat_Log"
        verbose_name_plural = "Chat_Log"

    def enable_room(self):
        self.enabled = True
        self.save()

    def disable_room(self):
        self.enabled = False
        self.save()

    def expire_room(self):
        self.expired = True
        self.save()


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    name = models.CharField(max_length=10, blank=True)
    speaker = models.CharField(max_length=100, blank=True)
    message = models.TextField(verbose_name='Message')
    timestamp = models.DateTimeField(verbose_name='Message Timestamp', auto_now_add=True, db_index=True)

    def __str__(self):
        # return self.message
        return '[{timestamp}] {speaker}:'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return timezone.localtime(self.timestamp).strftime('%H:%M %p')

    def as_dict(self):
        return {'speaker': self.speaker, 'timestamp': self.formatted_timestamp}

    def get_created(self):
        return self.created.strftime('%p %I:%M')