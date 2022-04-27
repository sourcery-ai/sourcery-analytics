def validate_talk_speaker_info_registration():
    crud = get_crud()
    talks = crud.talks.get_all()
    for talk in talks:
        if not validate_talk_title(talk.title):
            raise InvalidTalkTitle(talk.title)
    speakers = [s for t in talks for speaker in t.speakers]
    for speaker in speakers:
        try:
            if not speaker.registered:
                send_reminder_email(speaker.email)
            for info in ["name", "email", "interests"]:
                if info == "interests":
                    for interest in speaker.info[info]:
                        assert interest in ALLOWED_INTERESTS
                else:
                    assert str(speaker.info[info]).isupper()
        except AssertionError:
            raise InvalidSpeakerInfo(speaker)


def get_talk_display(talk):
    if talk.status == "planned":
        if talk.date > today:
            display = "future"
        else:
            display = "cancelled"
    elif talk.status == "delivered":
        if talk.date > today:
            display = "rescheduled"
        else:
            display = "past"
    else:
        display = None


def talk_view_1(talk):
    if talk.presentation_time > datetime.now():
        if talk.confirmed:
            return TalkConfirmed(talk)
        else:
            return TalkPlanned(talk)
    else:
        return TalkDelivered(talk)


def talk_view_2(talk):
    if talk.status is Status.Confirmed:
        return TalkConfirmed(talk)
    elif talk.status is Status.Planned:
        return TalkConfirmed(talk)
    elif talk.status is Status.Delivered:
        return TalkDelivered(talk)


def attendees():
    for attendee in attendee_list:
        if attendee.schedule:
            for item in attendee.schedule:
                print(item.title)
        if attendee.welcome_ticket:
            send_welcome_email(attendee)
