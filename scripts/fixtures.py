"""Deterministic synthetic workouts; no private data, fabricated GPS, or upstream services."""

from datetime import UTC, datetime, time, timedelta

from fit_tool import FitFileBuilder
from fit_tool.profile.messages.activity_message import ActivityMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.messages.session_message import SessionMessage
from fit_tool.profile.messages.workout_message import WorkoutMessage
from fit_tool.profile.profile_type import Activity, FileType, Manufacturer

DEFINITIONS = [
    ('Harness Easy Run', 1, 0, 'Run', 900, 3000, 220, 142, None),
    ('Harness Commute Ride', 2, 0, 'Ride', 1200, 7000, 310, 132, 140),
    ('Harness Walk', 11, 0, 'Walk', 900, 1200, 70, 95, None),
    ('Harness Strength', 10, 20, 'WeightTraining', 1800, None, 200, None, None),
    ('Harness Yoga', 10, 43, 'Yoga', 1200, None, 90, None, None),
    ('Harness Swim', 5, 17, 'Swim', 900, 600, 150, 120, None),
    ('Harness Interval Run', 1, 0, 'Run', 1200, 4000, 280, 155, None),
    ('Harness Long Ride', 2, 0, 'Ride', 1800, 10000, 450, 145, 160),
]


def build_activity(name, start, *, sport=1, sub_sport=0, duration=600,
                   distance=2000, calories=150, heart_rate=None, power=None):
    builder = FitFileBuilder(auto_define=True)
    start_ms = round(start.timestamp() * 1000)
    end_ms = start_ms + duration * 1000
    identity = FileIdMessage()
    identity.type = FileType.ACTIVITY
    identity.manufacturer = Manufacturer.DEVELOPMENT
    identity.product = 0
    identity.time_created = start_ms
    builder.add(identity)
    workout = WorkoutMessage()
    workout.workout_name = name
    workout.workout_description = 'Synthetic Dreeve addon harness fixture. Not a real workout.'
    workout.sport = sport
    workout.num_valid_steps = 0
    builder.add(workout)
    # Sensor samples are synthetic test input. Coordinates are omitted so seeding
    # never depends on geocoding, route downloads, or an external weather API.
    if heart_rate or power:
        for elapsed in range(0, duration + 1, 30):
            record = RecordMessage()
            record.timestamp = start_ms + elapsed * 1000
            if distance is not None:
                record.distance = distance * elapsed / duration
            if heart_rate:
                record.heart_rate = heart_rate + (elapsed // 30) % 5
            if power:
                record.power = power + (elapsed // 30) % 10
                record.cadence = 85
            builder.add(record)
    lap, session = LapMessage(), SessionMessage()
    for message in (lap, session):
        message.message_index = 0
        message.timestamp = end_ms
        message.start_time = start_ms
        message.total_elapsed_time = duration
        message.total_timer_time = duration
        message.sport = sport
        message.sub_sport = sub_sport
        message.total_calories = calories
        if distance is not None:
            message.total_distance = distance
            message.avg_speed = distance / duration
        if heart_rate:
            message.avg_heart_rate = heart_rate + 2
            message.max_heart_rate = heart_rate + 4
        if power:
            message.avg_power = power + 5
    builder.add(lap)
    session.first_lap_index = 0
    session.num_laps = 1
    builder.add(session)
    activity = ActivityMessage()
    activity.timestamp = end_ms
    activity.total_timer_time = duration
    activity.num_sessions = 1
    activity.type = Activity.MANUAL
    builder.add(activity)
    return builder.build().to_bytes()


def seed_fixtures(end_date):
    for index, (name, sport, sub, expected, duration, distance, calories, hr, power) in enumerate(DEFINITIONS):
        start = datetime.combine(end_date - timedelta(days=(7 - index) * 2), time(9), tzinfo=UTC)
        yield {'filename': f'harness-seed-{index + 1:02}.fit', 'name': name, 'sport': expected,
               'distance': distance or 0, 'duration': duration, 'calories': calories,
               'has_samples': bool(hr or power)}, build_activity(
                   name, start, sport=sport, sub_sport=sub, duration=duration,
                   distance=distance, calories=calories, heart_rate=hr, power=power)
