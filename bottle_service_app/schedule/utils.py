from datetime import datetime

from schedule.models import DaySchedule, TimeBlock


def condense_daily_schedule(day_schedule_id):
    try:
        day_schedule = DaySchedule.objects.get(id=day_schedule_id)
    except DaySchedule.DoesNotExist:
        return False

    time_blocks = day_schedule.time_blocks.all()
    sorted_time_blocks = sorted(time_blocks, key=lambda tb: tb.start_time)
    condensed_time_blocks = []

    if len(sorted_time_blocks) > 0:
        cur_time_block = sorted_time_blocks[0]
        for next_time_block in sorted_time_blocks[1:]:
            if cur_time_block.end_time >= next_time_block.start_time:
                cur_time_block.end_time = max(cur_time_block.end_time, next_time_block.end_time)
            else:
                time_block = TimeBlock(start_time=cur_time_block.start_time, end_time=cur_time_block.end_time,
                                       day_schedule=cur_time_block.day_schedule)
                condensed_time_blocks.append(time_block)
                cur_time_block = next_time_block
        time_block = TimeBlock(start_time=cur_time_block.start_time, end_time=cur_time_block.end_time,
                                       day_schedule=cur_time_block.day_schedule)
        condensed_time_blocks.append(time_block)

    for time_block in time_blocks:
        time_block.delete()

    for time_block in condensed_time_blocks:
        time_block.save()
    return True


def validate_times(start_time, end_time):
    try:
        s_time = datetime.strptime(start_time, '%H:%M').time()
        e_time = datetime.strptime(end_time, '%H:%M').time()
    except ValueError:
        raise ValueError('Invalid time format')
    if s_time >= e_time:
        raise ValueError('Start time must be before end time')


def get_current_datetime():
    return datetime.now()


def get_daily_schedule(weekly_schedule, day):
    if weekly_schedule is None:
        raise Exception('Weekly schedule cannot be null')
    if day is None:
        raise Exception('Day cannot be null')
    if day == 1:
        return weekly_schedule.monday
    elif day == 2:
        return weekly_schedule.tuesday
    elif day == 3:
        return weekly_schedule.wednesday
    elif day == 4:
        return weekly_schedule.thursday
    elif day == 5:
        return weekly_schedule.friday
    elif day == 6:
        return weekly_schedule.saturday
    elif day == 7:
        return weekly_schedule.sunday
    else:
        raise Exception('Invalid day')


def is_within_operational_hours(weekly_schedule, time=get_current_datetime()):
    if weekly_schedule is None:
        return False
    day_of_week = time.isoweekday()
    time_time = time.time()
    day_schedule = get_daily_schedule(weekly_schedule, day_of_week)
    for time_block in day_schedule.time_blocks.all():
        if time_block.start_time <= time_time < time_block.end_time:
            return True
    return False


# def operation_daily_schedule(day_schedule_1, day_schedule_2, operational_day_schedule):
#     if day_schedule_1 is None or day_schedule_2 is None:
#         for time_block in org_operational_day.all():
#             time_block.delete()
#         return None
#
#     # operational_day_schedule = DaySchedule.objects.create()
#
#     time_blocks_1 = day_schedule_1.time_blocks.all()
#     time_blocks_2 = day_schedule_2.time_blocks.all()
#     sorted_time_blocks_1 = sorted(time_blocks_1, key=lambda tb: tb.start_time)
#     sorted_time_blocks_2 = sorted(time_blocks_2, key=lambda tb: tb.start_time)
#     overlapping_time_blocks = []
#
#     if len(sorted_time_blocks_1) > 0 and len(sorted_time_blocks_2) > 0:
#         i = 0
#         j = 0
#         cur_time_block_1 = sorted_time_blocks_1[i]
#         cur_time_block_2 = sorted_time_blocks_2[j]
#         while i < len(sorted_time_blocks_1) and j < len(sorted_time_blocks_2):
#             lower_bound = max(cur_time_block_1.start_time, cur_time_block_2.start_time)
#             upper_bound = min(cur_time_block_1.end_time, cur_time_block_2.end_time)
#             if lower_bound < upper_bound:
#                 TimeBlock.objects.create(start_time=lower_bound, end_time=upper_bound,
#                                          day_schedule=operational_day_schedule)
#             if cur_time_block_1.end_time < cur_time_block_2.end_time:
#                 i += 1
#                 if i < len(sorted_time_blocks_1):
#                     cur_time_block_1 = sorted_time_blocks_1[i]
#             elif cur_time_block_1.end_time > cur_time_block_2.end_time:
#                 j += 1
#                 if j < len(sorted_time_blocks_2):
#                     cur_time_block_2 = sorted_time_blocks_2[j]
#             else:
#                 i += 1
#                 if i < len(sorted_time_blocks_1):
#                     cur_time_block_1 = sorted_time_blocks_1[i]
#                 j += 1
#                 if j < len(sorted_time_blocks_2):
#                     cur_time_block_2 = sorted_time_blocks_2[j]
#
#     for time_block in org_operational_day.all():
#         time_block.delete()
#
#     return operational_day_schedule
