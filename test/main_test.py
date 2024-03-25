from datetime import datetime, timedelta
import unittest

import pytz

from ev_flex_metric import main
from ev_flex_metric.main import BlockMetadata, ChargingSession, EnergyProfile, EvFlexMetricProfile, \
    ElaadChargingSession, to_energy_profile_using_default_charge_behaviour, ValuesInBlockProfile
from ev_flex_metric.ranges import IntRangeInBlock, DecimalRangeInBlock


class BlockMetadataTest(unittest.TestCase):
    def test__block_metadata_init__not_aligned_with_step_duration(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=15)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            BlockMetadata(start_time, end_time, step_duration)

    def test__block_metadata_init__correct(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=19)
        step_duration = timedelta(minutes=15)

        # Act
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        # Assert
        self.assertEqual(block_metadata.num_of_blocks, 4)
        self.assertEqual(block_metadata.step_duration, timedelta(minutes=15))
        self.assertEqual(block_metadata.start_time, datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19))
        self.assertEqual(block_metadata.end_time, datetime(year=2022, month=3, day=1, hour=14, minute=0, second=19))

    def test__convert_to_instant_in_block__correct_in_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=19)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        instant = datetime(year=2022, month=3, day=1, hour=13, minute=30, second=19)

        # Act
        instant_in_block = block_metadata.convert_to_instant_in_block(instant)

        # Assert
        self.assertEqual(instant_in_block, 3.0)

    def test__convert_to_instant_in_block__correct_after_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=19)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        instant = datetime(year=2022, month=3, day=1, hour=14, minute=35, second=19)

        # Act
        instant_in_block = block_metadata.convert_to_instant_in_block(instant)

        # Assert
        self.assertEqual(instant_in_block, 9.5)

    def test__convert_to_instant_in_block__correct_before_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=19)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=19)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        instant = datetime(year=2022, month=3, day=1, hour=12, minute=35, second=19)

        # Act
        instant_in_block = block_metadata.convert_to_instant_in_block(instant)

        # Assert
        self.assertEqual(instant_in_block, -2.5)

    def test__convert_to_range_in_block_decimal__correct_during_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=13, minute=35, second=0)
        end = datetime(year=2022, month=3, day=1, hour=13, minute=40, second=0)

        # Act
        range_in_block = block_metadata.convert_to_range_in_block_decimal(start, end)

        # Assert
        self.assertEqual(range_in_block.start, 3.5)
        self.assertEqual(range_in_block.end, 4.0)

    def test__convert_to_range_in_block_decimal__correct_before_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=12, minute=35, second=0)
        end = datetime(year=2022, month=3, day=1, hour=12, minute=55, second=0)

        # Act
        range_in_block = block_metadata.convert_to_range_in_block_decimal(start, end)

        # Assert
        self.assertEqual(range_in_block.start, -2.5)
        self.assertEqual(range_in_block.end,-0.5)

    def test__convert_to_range_in_block_decimal__correct_after_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        end = datetime(year=2022, month=3, day=1, hour=17, minute=0, second=0)

        # Act
        range_in_block = block_metadata.convert_to_range_in_block_decimal(start, end)

        # Assert
        self.assertEqual(range_in_block.start, 6.0)
        self.assertEqual(range_in_block.end, 24.0)

    def test__convert_to_range_in_block_int__correct(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end = datetime(year=2022, month=3, day=1, hour=13, minute=50, second=0)

        # Act
        int_block_in_range = block_metadata.convert_to_range_in_block_int(start, end)

        # Assert
        self.assertEqual(int_block_in_range, IntRangeInBlock(0, 5))

    def test__convert_to_range_in_block_int__start_does_not_line_up(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=1)
        end = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            block_metadata.convert_to_range_in_block_int(start, end)

    def test__convert_to_range_in_block_int__end_does_not_line_up(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)
        start = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end = datetime(year=2022, month=3, day=1, hour=13, minute=59, second=59)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            block_metadata.convert_to_range_in_block_int(start, end)

    def test__overlaps__correct_true(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        start_range = datetime(year=2022, month=3, day=1, hour=12, minute=0, second=0)
        end_range = datetime(year=2022, month=3, day=1, hour=13, minute=1, second=0)
        # Act
        result = block_metadata.overlaps(start_range, end_range)

        # Assert
        self.assertTrue(result)

    def test__overlaps__correct_false(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        start_range = datetime(year=2022, month=3, day=1, hour=12, minute=0, second=0)
        end_range = datetime(year=2022, month=3, day=1, hour=12, minute=59, second=59)
        # Act
        result = block_metadata.overlaps(start_range, end_range)

        # Assert
        self.assertFalse(result)

    def test__overlaps__left_touches_right(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        start_range = datetime(year=2022, month=3, day=1, hour=12, minute=0, second=0)
        end_range = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        # Act
        overlaps = block_metadata.overlaps(start_range, end_range)

        # Assert
        self.assertFalse(overlaps)


class ValuesInBlockProfileTest(unittest.TestCase):
    def test__normalized_index_for_block_num__happy_path(self):
        # Arrange
        range_in_block = IntRangeInBlock(2, 5)
        values = [2, 3, 4]
        profile = ValuesInBlockProfile(range_in_block, values)

        # Act
        index = profile.normalized_index_for_block_num(3)

        # Assert
        self.assertEqual(index, 1)

    def test__contains_value_for_block_num__true(self):
        # Arrange
        range_in_block = IntRangeInBlock(2, 5)
        values = [2, 3, 4]
        profile = ValuesInBlockProfile(range_in_block, values)

        # Act
        result = profile.contains_value_for_block_num(3)

        # Assert
        self.assertTrue(result)

    def test__contains_value_for_block_num__false_after(self):
        # Arrange
        range_in_block = IntRangeInBlock(2, 5)
        values = [2, 3, 4]
        profile = ValuesInBlockProfile(range_in_block, values)

        # Act
        result = profile.contains_value_for_block_num(5)

        # Assert
        self.assertFalse(result)

    def test__contains_value_for_block_num__before(self):
        # Arrange
        range_in_block = IntRangeInBlock(2, 5)
        values = [2, 3, 4]
        profile = ValuesInBlockProfile(range_in_block, values)

        # Act
        result = profile.contains_value_for_block_num(1)

        # Assert
        self.assertFalse(result)


class EnergyProfileTest(unittest.TestCase):
    def test__total_energy__correct(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.total_energy

        # Assert
        expected_total_energy = 12
        self.assertEqual(total_energy, expected_total_energy)

    def test__energy_between__correct_partial_range(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        between = IntRangeInBlock(2, 3)

        # Act
        energy_between = energy_profile.energy_between(between)

        # Assert
        self.assertEqual(energy_between, 4)

    def test__energy_between__correct_full_range(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        between = IntRangeInBlock(1, 4)

        # Act
        energy_between = energy_profile.energy_between(between)

        # Assert
        self.assertEqual(energy_between, 12)

    def test__energy_between__correct_on_start(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        between = IntRangeInBlock(1, 3)

        # Act
        energy_between = energy_profile.energy_between(between)

        # Assert
        self.assertEqual(energy_between, 7)

    def test__energy_between__correct_on_end(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        between = IntRangeInBlock(2, 4)

        # Act
        energy_between = energy_profile.energy_between(between)

        # Assert
        self.assertEqual(energy_between, 9)

    def test__energy_at__correct_first(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.energy_at(1)

        # Assert
        expected_energy = 3
        self.assertEqual(total_energy, expected_energy)

    def test__energy_at__correct_middle(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.energy_at(2)

        # Assert
        expected_energy = 4
        self.assertEqual(total_energy, expected_energy)

    def test__energy_at__correct_last(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.energy_at(3)

        # Assert
        expected_energy = 5
        self.assertEqual(total_energy, expected_energy)

    def test__energy_at__out_of_bounds(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act / Assert
        with self.assertRaises(RuntimeError):
            energy_profile.energy_at(4)

    def test__mask_int__left_overlap(self):
        # Arrange
        range_int = IntRangeInBlock(0, 3)
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.mask_int(range_int)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(1, 3), [3, 4])
        self.assertEqual(total_energy, expected_energy)

    def test__mask_int__right_overlap(self):
        # Arrange
        range_int = IntRangeInBlock(2, 6)
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.mask_int(range_int)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(2, 4), [4, 5])
        self.assertEqual(total_energy, expected_energy)

    def test__mask_int__contained(self):
        # Arrange
        range_int = IntRangeInBlock(0, 6)
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.mask_int(range_int)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        self.assertEqual(total_energy, expected_energy)

    def test__mask_int__contains(self):
        # Arrange
        range_int = IntRangeInBlock(2, 3)
        energy_profile = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])

        # Act
        total_energy = energy_profile.mask_int(range_int)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(2, 3), [4])
        self.assertEqual(total_energy, expected_energy)

    def test__split_on_int__no_overlap_right(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(1, 2)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        self.assertIsNone(result_left)
        expected_energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])
        self.assertEqual(expected_energy_profile, result_right)

    def test__split_on_int__no_overlap_left(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(4, 5)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        self.assertIsNone(result_right)
        expected_energy_profile = EnergyProfile(IntRangeInBlock(2, 4), [3, 4])
        self.assertEqual(expected_energy_profile, result_left)

    def test__split_on_int__start_on_left(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(2, 3)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        self.assertIsNone(result_left)
        expected_energy_profile = EnergyProfile(IntRangeInBlock(3, 5), [4, 5])
        self.assertEqual(expected_energy_profile, result_right)

    def test__split_on_int__end_on_right(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(4, 5)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        self.assertIsNone(result_right)
        expected_energy_profile = EnergyProfile(IntRangeInBlock(2, 4), [3, 4])
        self.assertEqual(expected_energy_profile, result_left)

    def test__split_on_int__in_middle(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(3, 4)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        expected_energy_profile_left = EnergyProfile(IntRangeInBlock(2, 3), [3])
        self.assertEqual(expected_energy_profile_left, result_left)
        expected_energy_profile_right = EnergyProfile(IntRangeInBlock(4, 5), [5])
        self.assertEqual(expected_energy_profile_right, result_right)

    def test__split_on_int__full_overlap(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        split_on_range = IntRangeInBlock(2, 5)

        # Act
        result_left, result_right = energy_profile.split_on_int(split_on_range)

        # Assert
        self.assertIsNone(result_left)
        self.assertIsNone(result_right)

    def test__profile_concat_right__happy_path(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        to_concat = EnergyProfile(IntRangeInBlock(5, 8), [6, 7, 8])

        # Act
        result_concat = energy_profile.profile_concat_right(to_concat)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(2, 8), [3, 4, 5, 6, 7, 8])
        self.assertEqual(result_concat, expected_energy_profile)

    def test__profile_concat_right__not_aligned_left(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        to_concat = EnergyProfile(IntRangeInBlock(1, 4), [6, 7, 8])

        # Act / Assert
        with self.assertRaises(RuntimeError):
            energy_profile.profile_concat_right(to_concat)

    def test__profile_concat_right__not_aligned_right(self):
        # Arrange
        energy_profile = EnergyProfile(IntRangeInBlock(2, 5), [3, 4, 5])

        to_concat = EnergyProfile(IntRangeInBlock(6, 9), [6, 7, 8])

        # Act / Assert
        with self.assertRaises(RuntimeError):
            energy_profile.profile_concat_right(to_concat)

    def test__profile_addition__no_overlap(self):
        # Arrange
        energy_profile_1 = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        energy_profile_2 = EnergyProfile(IntRangeInBlock(5, 7), [6, 9])

        # Act
        total_energy = energy_profile_1.profile_addition(energy_profile_2)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(1, 7), [3, 4, 5, 0, 6, 9])
        self.assertEqual(total_energy, expected_energy)

    def test__profile_addition__overlap(self):
        # Arrange
        energy_profile_1 = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        energy_profile_2 = EnergyProfile(IntRangeInBlock(3, 5), [6, 9])

        # Act
        total_energy = energy_profile_1.profile_addition(energy_profile_2)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(1, 5), [3, 4, 11, 9])
        self.assertEqual(total_energy, expected_energy)

    def test__profile_addition__contained(self):
        # Arrange
        energy_profile_1 = EnergyProfile(IntRangeInBlock(1, 4), [3, 4, 5])
        energy_profile_2 = EnergyProfile(IntRangeInBlock(2, 3), [6])

        # Act
        total_energy = energy_profile_1.profile_addition(energy_profile_2)

        # Assert
        expected_energy = EnergyProfile(IntRangeInBlock(1, 4), [3, 10, 5])
        self.assertEqual(total_energy, expected_energy)


class ChargingSessionTest(unittest.TestCase):
    def test__init__session_end_out_of_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 4 * [(20 * 3_600_000) / 4]  # 20 kWh per timestep
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 6)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__session_start_out_of_block(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 4 * [(20 * 3_600_000) / 4]  # 20 kWh per timestep
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(-1, 5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__energy_session_start_outside_of_charging_session(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [0] * 5
        energy_session = IntRangeInBlock(0, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__energy_session_end_outside_of_charging_session(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [0] * 5
        energy_session = IntRangeInBlock(1, 6)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__loads_too_much_energy_whole_timestep(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds() + 1,
                                  max_charging_power_watt * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__loads_too_much_energy_partial_first_timestep(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt / 2 * step_duration.total_seconds() + 1,
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1.5, 5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__loads_too_much_energy_partial_last_timestep(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt * step_duration.total_seconds() ,
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt / 2 * step_duration.total_seconds() + 1]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 4.5)

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ChargingSession(charge_session,
                            max_charging_power_watt,
                            energy_profile,
                            block_metadata)

    def test__init__correct_partial_timesteps(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt / 2 * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt / 2 * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1.5, 4.5)

        # Act
        charging_session = ChargingSession(charge_session,
                                           max_charging_power_watt,
                                           energy_profile,
                                           block_metadata)

        # Assert
        self.assertEqual(charging_session.session, charge_session)
        self.assertEqual(charging_session.max_charging_power_watt, max_charging_power_watt)
        self.assertEqual(charging_session.energy_to_charge_profile, energy_profile)
        self.assertEqual(charging_session.meta_data, block_metadata)

    def test__can_charge_energy_in_step__partial_0_7(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt / 2 * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt / 2 * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1.3, 4.5)

        charging_session = ChargingSession(charge_session,
                                           max_charging_power_watt,
                                           energy_profile,
                                           block_metadata)

        # Act
        can_charge_joule = charging_session.can_charge_energy_in_step(1)

        # Assert
        self.assertEqual(can_charge_joule, 16_800_000)

    def test__can_charge_energy_in_step__partial_0_5(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt / 2 * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt / 2 * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1.3, 4.5)

        charging_session = ChargingSession(charge_session,
                                           max_charging_power_watt,
                                           energy_profile,
                                           block_metadata)

        # Act
        can_charge_joule = charging_session.can_charge_energy_in_step(4)

        # Assert
        self.assertEqual(can_charge_joule, 12_000_000)

    def test__can_charge_energy_in_step__full(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [max_charging_power_watt / 2 * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt * step_duration.total_seconds(),
                                  max_charging_power_watt / 2 * step_duration.total_seconds()]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1.3, 4.5)

        charging_session = ChargingSession(charge_session,
                                           max_charging_power_watt,
                                           energy_profile,
                                           block_metadata)

        # Act
        can_charge_joule = charging_session.can_charge_energy_in_step(2)

        # Assert
        self.assertEqual(can_charge_joule, 24_000_000)

    def test__non_flexible_energy_utilizing_whole_session__correct_2_ptu_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 4 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(0, 3)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 6.666_667 * 3_600_000, delta=2)

    def test__non_flexible_energy_utilizing_whole_session__correct_1_ptu_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 4 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(0, 2)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 0)

    def test__non_flexible_energy_utilizing_whole_session__correct_4_ptu_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 4 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(0, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 20 * 3_600_000)

    def test__non_flexible_energy_utilizing_whole_session__no_overlap_session_with_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [0, 0]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 2.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(3, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)

        # Assert
        self.assertIsNone(non_flex_energy_during_congestion)

    def test__non_flexible_energy_utilizing_after_congestion__charging_before_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 5 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(0, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(0, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_range = IntRangeInBlock(1, 3)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_after_congestion(flex_window, congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 6.666_667 * 3_600_000, delta=2)

    def test__non_flexible_energy_utilizing_after_congestion__charging_after_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 3 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(2, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(2, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_range = IntRangeInBlock(1, 3)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_after_congestion(flex_window, congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 1.666_667 * 3_600_000, delta=2)

    def test__non_flexible_energy_utilizing_after_congestion__no_after_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 3 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(2, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(2, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_after_congestion(flex_window, congestion_range)

        # Assert
        self.assertAlmostEqual(non_flex_energy_during_congestion, 15 * 3_600_000, delta=2)

    def test__non_flexible_energy_utilizing_after_congestion__no_overlap_with_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = 3 * [5 * 3_600_000]  # 5 kWh per timestep
        energy_session = IntRangeInBlock(2, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(2, 5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_range = IntRangeInBlock(5, 9)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_after_congestion(flex_window, congestion_range)

        # Assert
        self.assertIsNone(non_flex_energy_during_congestion)

    def test__non_flexible_energy_evenly_divided__correct_partial_charge_session(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [18_000_000, 24_000_000, 12_000_000]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 3.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)
        non_flex_energy_profile_during_congestion = charge_session.non_flexible_energy_evenly_divided(non_flex_energy_during_congestion,
                                                                                                      congestion_range)

        # Assert
        expected_non_flexible_energy = 30_000_000
        self.assertEqual(non_flex_energy_during_congestion, expected_non_flexible_energy)
        self.assertEqual(non_flex_energy_profile_during_congestion, EnergyProfile(IntRangeInBlock(2, 4),
                                                                                  [20_000_000, 10_000_000]))

    def test__non_flexible_energy_evenly_divided__correct_full_charge_session(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [18_000_000, 24_000_000, 12_000_000]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 4.0)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)
        non_flex_energy_profile_during_congestion = charge_session.non_flexible_energy_evenly_divided(non_flex_energy_during_congestion,
                                                                                                      congestion_range)

        # Assert
        expected_non_flexible_energy = 30_000_000
        self.assertEqual(non_flex_energy_during_congestion, expected_non_flexible_energy)
        self.assertEqual(non_flex_energy_profile_during_congestion, EnergyProfile(IntRangeInBlock(2, 4),
                                                                                  [15_000_000, 15_000_000]))

    def test__non_flexible_energy_evenly_divided__overlap_but_no_energy(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [18_000_000, 0, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 4.0)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)
        non_flex_energy_profile_during_congestion = charge_session.non_flexible_energy_evenly_divided(non_flex_energy_during_congestion,
                                                                                                      congestion_range)

        # Assert
        self.assertEqual(non_flex_energy_during_congestion, 0)
        self.assertEqual(non_flex_energy_profile_during_congestion, EnergyProfile(IntRangeInBlock(2, 4), [0.0, 0.0]))

    def test__non_flexible_energy_evenly_divided__no_overlap(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 6.666,667 Wh per 10 minutes or 26.666,668 Wh for 40 minutes
        energy_to_charge_joule = [18_000_000, 0, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 4.0)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(5, 6)

        # Act
        non_flex_energy_during_congestion = charge_session.non_flexible_energy_utilizing_whole_session(congestion_range)
        non_flex_energy_profile_during_congestion = charge_session.non_flexible_energy_evenly_divided(non_flex_energy_during_congestion,
                                                                                                      congestion_range)

        # Assert
        self.assertIsNone(non_flex_energy_during_congestion)
        self.assertIsNone(non_flex_energy_profile_during_congestion)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__default_only_charging_partial_ending(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [24_000_000, 24_000_000, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1, 3.5)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 36_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [18_000_000, 18_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__default_only_charging_full_ending(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [24_000_000, 24_000_000, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1, 4.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 24_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [12_000_000, 12_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__default_only_charging_slow_start(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [12_000_000, 24_000_000, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1, 4.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 12_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [6_000_000, 6_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__default_only_charging_partial_start(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [12_000_000, 24_000_000, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.5, 4.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 12_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [6_000_000, 6_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__capped_by_default_due_to_slow_start(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 24_000_000, 0]
        energy_session = IntRangeInBlock(1, 4)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.0, 3.5)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 14_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [2_000_000, 12_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__no_change(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 24_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.0, 3.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(1, 3)
        non_flex_energy_during_congestion = 26_000_000

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(non_flex_energy_during_congestion,
                                                                                                                       congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3),
                                                [2_000_000, 24_000_000])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging__partial_start_all_non_flex(self):
        # Arrange
        non_flex_energy_during_congestion = 15179999.0
        congestion_range = IntRangeInBlock(start=24, end=40)

        start_time = datetime(year=2020, month=6, day=3, hour=3, minute=0, second=0)
        end_time = datetime(year=2020, month=6, day=4, hour=3, minute=0, second=0)
        step_duration = timedelta(minutes=15)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        energy_profile = EnergyProfile(range_in_block=IntRangeInBlock(start=33, end=39),
                                       energy_per_block=[7259999.0, 7920000.0, 0.0, 0.0, 0.0, 0.0])

        max_charging_power_watt = 11_000
        charge_session_range = DecimalRangeInBlock(start=33.266666666666666, end=38.06666666666667)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        # Act
        energy_profile = charge_session.non_flexible_energy_evenly_divided_while_not_increasing_above_default_charging(
            non_flex_energy_during_congestion,
            congestion_range)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(start=33, end=39),
                                                [7259999.0, 7920000.0, 0.0, 0.0, 0.0, 0.0])

        self.assertEqual(expected_energy_profile, energy_profile)

    def test__charge_extra_energy_immediately__not_full_partial(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 24_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 3.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        to_charge = 17_000_000

        # Act
        extra_charge_energy_profile = charge_session.charge_extra_energy_immediately(energy_profile,
                                                                                     to_charge)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3), [19_000_000, 24_000_000])
        self.assertEqual(expected_energy_profile, extra_charge_energy_profile)

    def test__charge_extra_energy_immediately__full_partial(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 24_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 3.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        to_charge = 17_200_000

        # Act
        extra_charge_energy_profile = charge_session.charge_extra_energy_immediately(energy_profile,
                                                                                     to_charge)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3), [19_200_000, 24_000_000])
        self.assertEqual(expected_energy_profile, extra_charge_energy_profile)

    def test__charge_extra_energy_immediately__too_much_partial(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 24_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 3.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        to_charge = 17_200_001

        # Act / Assert
        with self.assertRaises(RuntimeError):
            charge_session.charge_extra_energy_immediately(energy_profile, to_charge)

    def test__charge_extra_energy_immediately__multiple_blocks(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 1_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 3.0)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        to_charge = 18_200_000

        # Act
        extra_charge_energy_profile = charge_session.charge_extra_energy_immediately(energy_profile,
                                                                                     to_charge)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3), [19_200_000, 2_000_000])
        self.assertEqual(expected_energy_profile, extra_charge_energy_profile)

    def test__charge_extra_energy_immediately__multiple_blocks_long(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [2_000_000, 1_000_000, 0, 0, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        to_charge = 180_200_000

        # Act
        extra_charge_energy_profile = charge_session.charge_extra_energy_immediately(energy_profile,
                                                                                     to_charge)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9), [19_200_000,
                                                                        24_000_000,
                                                                        24_000_000,
                                                                        24_000_000,
                                                                        24_000_000,
                                                                        24_000_000,
                                                                        24_000_000,
                                                                        20_000_000])
        self.assertEqual(expected_energy_profile, extra_charge_energy_profile)

    def test__shift_flexible_energy_after_congestion__no_non_flexible_energy_start_midway(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(2, 4)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9), [8_000_000, 0, 0, 24_000_000, 24_000_000, 10_000_000, 0, 0])
        self.assertEqual(expected_energy_profile, shifted_energy_profile)

    def test__shift_flexible_energy_after_congestion__no_non_flexible_energy_on_start(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(1, 3)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9), [0, 0, 24_000_000, 24_000_000, 18_000_000, 0, 0, 0])
        self.assertEqual(expected_energy_profile, shifted_energy_profile)

    def test__shift_flexible_energy_after_congestion__no_non_flexible_energy_on_end(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(7, 9)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9), [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0])
        self.assertEqual(expected_energy_profile, shifted_energy_profile)

    def test__shift_flexible_energy_after_congestion__congestion_whole_duration(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(1, 9)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9),
                                                [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0])
        self.assertEqual(expected_energy_profile, shifted_energy_profile)

    def test__shift_flexible_energy_after_congestion__congestion_no_overlap(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(9, 11)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9),
                                                [8_000_000, 24_000_000, 24_000_000, 10_000_000, 0, 0, 0, 0])
        self.assertEqual(expected_energy_profile, shifted_energy_profile)

    def test__shift_flexible_energy_after_congestion__no_flexible_energy(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=15, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        flex_window = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [19_200_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 20_400_000]
        energy_session = IntRangeInBlock(1, 9)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session_range = DecimalRangeInBlock(1.2, 8.85)
        charge_session = ChargingSession(charge_session_range,
                                         max_charging_power_watt,
                                         energy_profile,
                                         flex_window)

        congestion_steps = IntRangeInBlock(2, 3)

        # Act
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion_steps)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 9),
                                                [19_200_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 24_000_000, 20_400_000])
        self.assertEqual(expected_energy_profile.range_in_block, shifted_energy_profile.range_in_block)
        for expected, result in zip(expected_energy_profile.value_per_block, shifted_energy_profile.value_per_block):
            self.assertAlmostEqual(expected, result)

    def test__calculate_flex_metric__correct_no_energy_in_congestion(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [24_000_000, 0]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 2.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        ev_flex_profile = charge_session.calculate_flex_metric(congestion_range)

        # Assert
        expected_ev_flex_profile = EvFlexMetricProfile(IntRangeInBlock(2, 3), [0])
        self.assertEqual(ev_flex_profile, expected_ev_flex_profile)

    def test__calculate_flex_metric__correct_energy_in_congestion_partially_move_fully(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [0, 12_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 2.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        ev_flex_profile = charge_session.calculate_flex_metric(congestion_range)

        # Assert
        expected_ev_flex_profile = EvFlexMetricProfile(IntRangeInBlock(2, 3), [1])
        self.assertEqual(ev_flex_profile, expected_ev_flex_profile)

    def test__calculate_flex_metric__correct_energy_in_congestion_partially_cannot_move(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [24_000_000, 12_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 2.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        ev_flex_profile = charge_session.calculate_flex_metric(congestion_range)

        # Assert
        expected_ev_flex_profile = EvFlexMetricProfile(IntRangeInBlock(2, 3), [0])
        self.assertEqual(ev_flex_profile, expected_ev_flex_profile)

    def test__calculate_flex_metric__correct_energy_in_congestion_partially_can_move_partially(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [18_000_000, 12_000_000]
        energy_session = IntRangeInBlock(1, 3)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 2.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        ev_flex_profile = charge_session.calculate_flex_metric(congestion_range)

        # Assert
        expected_ev_flex_profile = EvFlexMetricProfile(IntRangeInBlock(2, 3), [0.5])
        self.assertEqual(ev_flex_profile, expected_ev_flex_profile)

    def test__calculate_flex_metric__correct_complex(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        max_charging_power_watt = 40_000  # Can charge 24.000.000 joule per 10 minutes / timestep
        energy_to_charge_joule = [20_000_000, 1, 12_000_000, 6_000_000]
        energy_session = IntRangeInBlock(1, 5)
        energy_profile = EnergyProfile(energy_session, energy_to_charge_joule)

        charge_session = DecimalRangeInBlock(1, 4.5)
        charge_session = ChargingSession(charge_session,
                                         max_charging_power_watt,
                                         energy_profile,
                                         block_metadata)

        congestion_range = IntRangeInBlock(2, 5)

        # Act
        ev_flex_profile = charge_session.calculate_flex_metric(congestion_range)

        # Assert
        expected_ev_flex_profile = EvFlexMetricProfile(IntRangeInBlock(2, 5), [0.2222222098765439] * 3)
        self.assertEqual(ev_flex_profile, expected_ev_flex_profile)


class ElaadChargingSessionTest(unittest.TestCase):
    def test__to_general_charging_session__has_charging_outside_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=12, minute=5, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=50, second=0)
        charging_time = timedelta(hours=1.5)
        charged_energy_kwh = 18
        max_charge_power_kw = 40
        elaad_session = ElaadChargingSession('1',
                                             charge_start_time,
                                             charge_end_time,
                                             charging_time,
                                             charged_energy_kwh,
                                             max_charge_power_kw)


        # Act
        general_charging_session = elaad_session.to_general_charging_session(block_metadata)

        # Assert
        expected_charge_session = ChargingSession(session=DecimalRangeInBlock(0.0, 6.0),
                                                  max_charging_power_watt=40_000,
                                                  energy_to_charge_profile=EnergyProfile(IntRangeInBlock(0, 6),
                                                                                         [7_200_000,
                                                                                          7_200_000,
                                                                                          7_200_000,
                                                                                          3_600_000,
                                                                                          0,
                                                                                          0]),
                                                  meta_data=block_metadata)

        self.assertEqual(general_charging_session, expected_charge_session)

    def test__to_general_charging_session__has_charging_inside_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=5, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=50, second=0)
        charging_time = timedelta(hours=0.5)
        charged_energy_kwh = 18
        max_charge_power_kw = 40
        elaad_session = ElaadChargingSession('1',
                                             charge_start_time,
                                             charge_end_time,
                                             charging_time,
                                             charged_energy_kwh,
                                             max_charge_power_kw)


        # Act
        general_charging_session = elaad_session.to_general_charging_session(block_metadata)

        # Assert
        expected_charge_session = ChargingSession(session=DecimalRangeInBlock(0.5, 5.0),
                                                  max_charging_power_watt=40_000,
                                                  energy_to_charge_profile=EnergyProfile(IntRangeInBlock(0, 5),
                                                                                         [10_800_000,
                                                                                          21_600_000,
                                                                                          21_600_000,
                                                                                          10_800_000,
                                                                                          0]),
                                                  meta_data=block_metadata)

        self.assertEqual(general_charging_session, expected_charge_session)

    def test__to_general_charging_session__is_charging_full_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        charging_time = timedelta(hours=1)
        charged_energy_kwh = 40
        max_charge_power_kw = 40
        elaad_session = ElaadChargingSession('1',
                                             charge_start_time,
                                             charge_end_time,
                                             charging_time,
                                             charged_energy_kwh,
                                             max_charge_power_kw)


        # Act
        general_charging_session = elaad_session.to_general_charging_session(block_metadata)

        # Assert
        expected_charge_session = ChargingSession(session=DecimalRangeInBlock(0, 6.0),
                                                  max_charging_power_watt=40_000,
                                                  energy_to_charge_profile=EnergyProfile(IntRangeInBlock(0, 6),
                                                                                         [24_000_000,
                                                                                          24_000_000,
                                                                                          24_000_000,
                                                                                          24_000_000,
                                                                                          24_000_000,
                                                                                          24_000_000]),
                                                  meta_data=block_metadata)

        self.assertEqual(general_charging_session, expected_charge_session)

    def test__from_line__correct(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:57,2019-03-01 12:08:04,"eabc4bb019389",3.62,1.75,1.87,4.859,3.64'

        # Act
        elaad_transaction = ElaadChargingSession.from_line(line)

        # Assert
        self.assertEqual(elaad_transaction.transaction_id, '1026840')
        self.assertEqual(elaad_transaction.utc_session_start,
                         datetime(year=2019, month=3, day=1, hour=8, minute=30, second=57, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.utc_session_stop,
                         datetime(year=2019, month=3, day=1, hour=12, minute=8, second=4, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.charging_time, timedelta(hours=1.75))
        self.assertEqual(elaad_transaction.charged_energy_kwh, 4.859)
        self.assertEqual(elaad_transaction.max_power_kw, 3.64)

    def test__from_line__average_power_above_max_charging_power(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.75,1.87,5.26,3.0'

        # Act
        elaad_transaction = ElaadChargingSession.from_line(line)

        # Assert
        self.assertEqual(elaad_transaction.transaction_id, '1026840')
        self.assertEqual(elaad_transaction.utc_session_start,
                         datetime(year=2019, month=3, day=1, hour=8, minute=30, second=00, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.utc_session_stop,
                         datetime(year=2019, month=3, day=1, hour=10, minute=15, second=12, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.charging_time, timedelta(hours=1, minutes=45, seconds=12))
        self.assertEqual(elaad_transaction.charged_energy_kwh, 5.26)
        self.assertEqual(elaad_transaction.max_power_kw, 3.0)

    def test__from_line__average_power__just_lower_than_significantly_above_max_charging_power(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.75,1.87,5.3025,3.0'

        # Act
        elaad_transaction = ElaadChargingSession.from_line(line)

        # Assert
        self.assertEqual(elaad_transaction.transaction_id, '1026840')
        self.assertEqual(elaad_transaction.utc_session_start,
                         datetime(year=2019, month=3, day=1, hour=8, minute=30, second=00, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.utc_session_stop,
                         datetime(year=2019, month=3, day=1, hour=10, minute=16, second=3, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.charging_time, timedelta(hours=1, minutes=46, seconds=3))
        self.assertEqual(elaad_transaction.charged_energy_kwh, 5.3025)
        self.assertEqual(elaad_transaction.max_power_kw, 3.0)

    def test__from_line__average_power__just_on_significantly_above_max_charging_power(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.75,1.87,5.3026,3.0'

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ElaadChargingSession.from_line(line)

    def test__from_line__average_power_exactly_max_charging_power(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.75,1.87,5.25,3.0'

        # Act
        elaad_transaction = ElaadChargingSession.from_line(line)

        # Assert
        self.assertEqual(elaad_transaction.transaction_id, '1026840')
        self.assertEqual(elaad_transaction.utc_session_start,
                         datetime(year=2019, month=3, day=1, hour=8, minute=30, second=00, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.utc_session_stop,
                         datetime(year=2019, month=3, day=1, hour=10, minute=15, second=0, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.charging_time, timedelta(hours=1.75))
        self.assertEqual(elaad_transaction.charged_energy_kwh, 5.25)
        self.assertEqual(elaad_transaction.max_power_kw, 3.0)

    def test__from_line__charge_time_is_longer_than_transaction_duration(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.76,1.87,5.25,3.0'

        # Act
        elaad_transaction = ElaadChargingSession.from_line(line)

        # Assert
        self.assertEqual(elaad_transaction.transaction_id, '1026840')
        self.assertEqual(elaad_transaction.utc_session_start,
                         datetime(year=2019, month=3, day=1, hour=8, minute=30, second=00, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.utc_session_stop,
                         datetime(year=2019, month=3, day=1, hour=10, minute=15, second=36, tzinfo=pytz.utc))
        self.assertEqual(elaad_transaction.charging_time, timedelta(hours=1, minutes=45, seconds=36))
        self.assertEqual(elaad_transaction.charged_energy_kwh, 5.25)
        self.assertEqual(elaad_transaction.max_power_kw, 3.0)

    def test__from_line__charge_time_is_significantly_longer_than_transaction_duration(self):
        # Arrange
        line = '"19","1026840","BU321","BU321-1",2019-03-01 08:30:00,2019-03-01 10:15:00,"eabc4bb019389",3.62,1.77,1.87,5.25,3.0'

        # Act / Assert
        with self.assertRaises(RuntimeError):
            ElaadChargingSession.from_line(line)

        # TODO NOTE FOR SELF:
        # There are 2 EV flex metrics possible:
        #   1. Currently implemented, create a single EV flex factor that describes how much energy each timestep during congestion may be reduced.
        #   2. Distribute the non-flexible energy evenly over all timesteps in congestion. Issue may happen that a step which uses 1 energy originally may get energy assigned which creates a large, negative EV flex metrics
        #   3. Perhaps a solution for #2, distribute the non-flexible energy up to the original energy used and as evenly as possible.


class GlobalTest(unittest.TestCase):
    def test__to_energy_profile__correct_within_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charging_time = timedelta(minutes=25)
        charged_energy_kwh = 16.66666667
        max_charge_power_kw = 40
        charge_session = DecimalRangeInBlock(0, 4)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(0, 4),
                                                [24000000.0, 24000000.0, 12000000.0, 0])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__correct_partially_outside_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=12, minute=0, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=40, second=0)
        charging_time = timedelta(hours=1, minutes=25)
        charged_energy_kwh = 16.66666667
        max_charge_power_kw = 40
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)
        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(-6, 4),
                                                [7058823.53082353] * 8 + [3529411.765411765, 0])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__less_then_one_timestep(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=3, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=7, second=0)
        charging_time = timedelta(minutes=3.5)
        charged_energy_kwh = 2
        max_charge_power_kw = 40
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(0, 1), [7199999.999999999])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__one_timestep(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=10, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=20, second=0)
        charging_time = timedelta(minutes=10)
        charged_energy_kwh = 2
        max_charge_power_kw = 40
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 2), [7_200_000])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__less_than_one_timestep_across_timesteps(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=15, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=25, second=0)
        charging_time = timedelta(minutes=9)
        charged_energy_kwh = 2
        max_charge_power_kw = 40
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 3), [4_000_000, 3_200_000])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__bug1(self):
        # Arrange
        block_start_time = datetime(year=2019, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2019, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=15)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2019, month=3, day=1, hour=13, minute=58, second=59)
        charge_end_time = datetime(year=2019, month=3, day=1, hour=14, minute=13, second=23)
        charging_time = timedelta(seconds=864)
        charged_energy_kwh = 2.38
        # Average charge power watt = 9_916.6666666666666666666666666667
        max_charge_power_kw = 9.951
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(3, 5), [604_916.6668649999, 7_963_083.333135])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__bug2(self):
        # Arrange
        block_start_time = datetime(year=2019, month=3, day=2, hour=10, minute=0, second=0)
        block_end_time = datetime(year=2019, month=3, day=2, hour=11, minute=0, second=0)
        step_duration = timedelta(minutes=15)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2019, month=3, day=2, hour=10, minute=20, second=21)
        charge_end_time = datetime(year=2019, month=3, day=2, hour=10, minute=29, second=57)
        charging_time = timedelta(seconds=576)
        charged_energy_kwh = 0.64
        max_charge_power_kw = 4.028
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(1, 2), [2_304_000])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__to_energy_profile__correct_starts_and_ends_partially_in_block(self):
        # Arrange
        block_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        block_end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(block_start_time, block_end_time, step_duration)

        charge_start_time = datetime(year=2022, month=3, day=1, hour=13, minute=5, second=0)
        charge_end_time = datetime(year=2022, month=3, day=1, hour=13, minute=50, second=0)
        charging_time = timedelta(minutes=30)
        charged_energy_kwh = 18
        max_charge_power_kw = 40
        charge_session = block_metadata.convert_to_range_in_block_decimal(charge_start_time,
                                                                          charge_end_time)

        # Act
        energy_profile = to_energy_profile_using_default_charge_behaviour(charge_session,
                                                                          block_metadata,
                                                                          charged_energy_kwh,
                                                                          charging_time,
                                                                          max_charge_power_kw)

        # Assert
        expected_energy_profile = EnergyProfile(IntRangeInBlock(0, 5),
                                                [10_800_000, 21600000, 21600000, 10_800_000, 0])
        self.assertEqual(energy_profile, expected_energy_profile)

    def test__calculate_ev_flex_metric__correct(self):
        # Arrange
        start_time = datetime(year=2022, month=3, day=1, hour=13, minute=0, second=0)
        end_time = datetime(year=2022, month=3, day=1, hour=14, minute=0, second=0)
        step_duration = timedelta(minutes=10)
        block_metadata = BlockMetadata(start_time, end_time, step_duration)

        charge_session_1 = ChargingSession(session=DecimalRangeInBlock(1, 5),
                                           max_charging_power_watt=40_000,
                                           energy_to_charge_profile=EnergyProfile(IntRangeInBlock(1, 5),
                                                                                  [6.66 * 3_600_000,
                                                                                   6.66 * 3_600_000,
                                                                                   3.335 * 3_600_000,
                                                                                   0]),
                                           meta_data=block_metadata)
        charge_session_2 = ChargingSession(session=DecimalRangeInBlock(0, 3.5),
                                           max_charging_power_watt=40_000,
                                           energy_to_charge_profile=EnergyProfile(IntRangeInBlock(0, 4),
                                                                                  [3.335 * 3_600_000,
                                                                                   3.335 * 3_600_000,
                                                                                   0,
                                                                                   3.33 * 3_600_000]),
                                           meta_data=block_metadata)
        charge_session_3 = ChargingSession(session=DecimalRangeInBlock(3.2, 5.8),
                                           max_charging_power_watt=40_000,
                                           energy_to_charge_profile=EnergyProfile(IntRangeInBlock(3, 6),
                                                                                  [4 * 3_600_000,
                                                                                   3 * 3_600_000,
                                                                                   0]),
                                           meta_data=block_metadata)

        congestion_range = IntRangeInBlock(1, 5)

        # Act
        ev_flex_metric_profile = main.calculate_ev_flex_metric(block_metadata,
                                                               congestion_range,
                                                               [charge_session_1,
                                                                charge_session_2,
                                                                charge_session_3])

        # Assert
        expected_non_flex_energy_1 = 16.655      * 3_600_000
        expected_non_flex_energy_2 = 3.333333333 * 3_600_000
        expected_non_flex_energy_3 = 1.666666667 * 3_600_000

        self.assertAlmostEqual(charge_session_1.non_flexible_energy_utilizing_whole_session(congestion_range),
                               expected_non_flex_energy_1,
                               delta=0.00001)
        self.assertAlmostEqual(charge_session_2.non_flexible_energy_utilizing_whole_session(congestion_range),
                               expected_non_flex_energy_2,
                               delta=0.01)
        self.assertAlmostEqual(charge_session_3.non_flexible_energy_utilizing_whole_session(congestion_range),
                               expected_non_flex_energy_3,
                               delta=0.01)

        expected_non_flex_profile_1 = EnergyProfile(IntRangeInBlock(1, 5),
                                                    [14989500.0] * 4)
        expected_non_flex_profile_2 = EnergyProfile(IntRangeInBlock(1, 4),
                                                    [4_800_000,
                                                     4_800_000,
                                                     2_400_000])
        expected_non_flex_profile_3 = EnergyProfile(IntRangeInBlock(3, 5),
                                                    [2_666_666.666666668,
                                                     3_333_333.333333336])
        self.assertEqual(charge_session_1.non_flexible_energy_evenly_divided(expected_non_flex_profile_1.total_energy,
                                                                             congestion_range),
                         expected_non_flex_profile_1)
        self.assertEqual(charge_session_2.non_flexible_energy_evenly_divided(expected_non_flex_profile_2.total_energy,
                                                                             congestion_range),
                         expected_non_flex_profile_2)
        self.assertEqual(charge_session_3.non_flexible_energy_evenly_divided(expected_non_flex_profile_3.total_energy,
                                                                             congestion_range),
                         expected_non_flex_profile_3)

        expected_non_flex_profile = EnergyProfile(IntRangeInBlock(1, 5),
                                                  [19_789_500,
                                                   19_789_500,
                                                   20_056_166.66666668,
                                                   18_322_833.333333336])
        expected_default_profile = EnergyProfile(IntRangeInBlock(1, 5),
                                                 [(6.66 + 3.335)     * 3_600_000,  # 35_982_000
                                                  (6.66)             * 3_600_000,  # 23_976_000
                                                  (3.335 + 3.33 + 4) * 3_600_000,  # 38_394_000
                                                  (3)                * 3_600_000])  # 10_800_000

        expected_ev_metric = EvFlexMetricProfile(IntRangeInBlock(1, 5),
                                                 [ 0.45001667500416875, #(35_982_000 - 19_789_500) / 35_982_000,
                                                   0.1746121121121121,  # (23_976_000 - 19_789_500) / 23_976_000,
                                                   0.47762237155111037, # (38_394_000 - 20_056_166.66666668) / 38_394_000,
                                                  -0.6965586419753089]) # (10_800_000 - 18_322_833.333333336) / 10_800_000])
        self.assertEqual(ev_flex_metric_profile, expected_ev_metric)

