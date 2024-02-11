import datetime

from django.test import TestCase

from schedule.models import DaySchedule, TimeBlock
from schedule.utils import validate_times, condense_daily_schedule
from django.db import models

# Create your tests here.
class ValidateTimesTest(TestCase):

    def test_valid_start_and_end_times(self):
        start_time = '09:00'
        end_time = '10:00'
        self.assertIsNone(validate_times(start_time, end_time))

    def test_missing_start_time(self):
        start_time = ''
        end_time = '10:00'
        with self.assertRaises(ValueError):
            validate_times(start_time, end_time)

    def test_missing_end_time(self):
        start_time = '09:00'
        end_time = ''
        with self.assertRaises(ValueError):
            validate_times(start_time, end_time)

    def test_wrong_format_times(self):
        start_time = '09:00'
        end_time = '30:00'
        with self.assertRaises(ValueError):
            validate_times(start_time, end_time)

    def test_wrong_order_times(self):
        start_time = '09:00'
        end_time = '05:00'
        with self.assertRaises(ValueError):
            validate_times(start_time, end_time)

    def test_same_times(self):
        start_time = '09:00'
        end_time = '09:00'
        with self.assertRaises(ValueError):
            validate_times(start_time, end_time)


class CondenseDailyScheduleTest(TestCase):
    def test_valid_day_schedule_id(self):
        # Create a DaySchedule object with multiple TimeBlock objects
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='10:00',
                                               end_time='11:00')
        time_block3 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='11:00',
                                               end_time='12:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the time blocks are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 1)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(12, 0))

    def test_no_time_blocks(self):
        # Create a DaySchedule object with no TimeBlock objects
        day_schedule = DaySchedule.objects.create()

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the function returns True without modifying anything
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 0)

        def test_single_time_block(self):
            # Create a DaySchedule object with a single TimeBlock object
            day_schedule = DaySchedule.objects.create()
            time_block = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                                  end_time='10:00')

            # Call the condense_daily_schedule function
            result = condense_daily_schedule(day_schedule.id)

            # Check if the function returns True without modifying anything
            self.assertTrue(result)
            self.assertEqual(day_schedule.time_blocks.count(), 1)
            self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
            self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(10, 0))

    def test_invalid_day_schedule_id(self):
        # Call the condense_daily_schedule function with an invalid day_schedule_id
        result = condense_daily_schedule(999)

        # Check if the function returns False
        self.assertFalse(result)

    def test_overlapping_time_blocks(self):
        # Create a DaySchedule object with overlapping TimeBlock objects
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='09:00',
                                               end_time='11:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the overlapping time blocks are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 1)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(11, 0))

    def test_start_time_equal_to_end_time(self):
        # Create a DaySchedule object with TimeBlock objects where start_time is equal to end_time
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='10:00',
                                               end_time='12:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the time blocks with start_time equal to end_time are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 1)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(12, 0))

    def test_equal_time(self):
        # Create a DaySchedule object with TimeBlock objects where start_time is equal to end_time
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the time blocks with start_time equal to end_time are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 1)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(10, 0))

    def test_dont_condense_time(self):
        # Create a DaySchedule object with TimeBlock objects where start_time is equal to end_time
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='10:01',
                                               end_time='12:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the time blocks with start_time equal to end_time are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 2)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(10, 0))
        self.assertEqual(day_schedule.time_blocks.all()[1].start_time, datetime.time(10, 1))
        self.assertEqual(day_schedule.time_blocks.all()[1].end_time, datetime.time(12, 0))

    def test_valid_day_schedule_id_out_of_order(self):
        # Create a DaySchedule object with multiple TimeBlock objects
        day_schedule = DaySchedule.objects.create()
        time_block1 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='10:00',
                                               end_time='11:00')
        time_block2 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='11:00',
                                               end_time='12:00')
        time_block3 = TimeBlock.objects.create(day_schedule=day_schedule, start_time='08:00',
                                               end_time='10:00')

        # Call the condense_daily_schedule function
        result = condense_daily_schedule(day_schedule.id)

        # Check if the time blocks are properly condensed
        self.assertTrue(result)
        self.assertEqual(day_schedule.time_blocks.count(), 1)
        self.assertEqual(day_schedule.time_blocks.first().start_time, datetime.time(8, 0))
        self.assertEqual(day_schedule.time_blocks.first().end_time, datetime.time(12, 0))
