from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant



def video_conf(request):
    return render(request, 'video/video_conf.html')

# Create a new Twilio Room
def create_video(request):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    # Initialize the Twilio client.
    client = Client(account_sid, auth_token)

    try:
        client.video.rooms.create(unique_name='test-video-room')
        from .models import Room
        Room.objects.get_or_create(group_name='test-video-room')
        return redirect('/')
    except:
        return redirect('/')

# Enter Video Room
@login_required
def video_room(request, room_name):
    account_sid = settings.TWILIO_ACCOUNT_SID
    api_key_sid = settings.TWILIO_API_KEY
    api_key_secret = settings.TWILIO_API_SECRET

    if room_name == 'test-video-room':
        identity = str(timezone.now())
    else:
        identity = room_name + str(request.user.id)

    try:
        token = AccessToken(account_sid, api_key_sid, api_key_secret, identity=identity)
        grant = VideoGrant(room=room_name)
    except:
        messages.warning(request, "Reservation hasn't started yet or is expired")
        return redirect('mentee_reservation')

    token.add_grant(grant)
    jwt = token.to_jwt()
    decoded = jwt.decode('utf-8')

    return render(request, 'video/room.html', {'token': decoded,
                                               'messages': messages,
                                               'user': request.user,
                                               'room_name': room_name})

# Close on-going Twilio Conference
def kick_video(request):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    try:
        client.video.rooms('test-video-room').fetch().update(status='completed')
        return redirect('/')
    except:
        return redirect('/')


@csrf_exempt
def video_callback(request):
    return HttpResponse(content_type="application/x-www-urlencoded") 