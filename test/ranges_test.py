import unittest

from ev_flex_metric.ranges import IntRangeInBlock, DecimalRangeInBlock


class RangeInBlockTest(unittest.TestCase):
    def test__overlaps__left_before_right(self):
        # Arrange
        left = IntRangeInBlock(1, 3)
        right = IntRangeInBlock(3, 5)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertFalse(overlaps)

    def test__overlaps__left_after_right(self):
        # Arrange
        left = IntRangeInBlock(3, 5)
        right = IntRangeInBlock(1, 3)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertFalse(overlaps)

    def test__overlaps__left_partially_overlaps_right(self):
        # Arrange
        left = IntRangeInBlock(1, 3)
        right = IntRangeInBlock(2, 4)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertTrue(overlaps)

    def test__overlaps__right_partially_overlaps_left(self):
        # Arrange
        left = IntRangeInBlock(2, 4)
        right = IntRangeInBlock(1, 3)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertTrue(overlaps)

    def test__overlaps__left_fully_overlaps_right(self):
        # Arrange
        left = IntRangeInBlock(0, 4)
        right = IntRangeInBlock(1, 3)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertTrue(overlaps)

    def test__overlaps__left_is_right(self):
        # Arrange
        left = IntRangeInBlock(0, 4)
        right = IntRangeInBlock(0, 4)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertTrue(overlaps)

    def test__overlaps__right_fully_overlaps_left(self):
        # Arrange
        left = IntRangeInBlock(1, 4)
        right = IntRangeInBlock(0, 6)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertTrue(overlaps)

    def test__overlaps__left_touches_right(self):
        # Arrange
        left = DecimalRangeInBlock(-10.5, 4.0)
        right = IntRangeInBlock(4, 6)

        # Act
        overlaps = left.overlaps(right)

        # Assert
        self.assertFalse(overlaps)

    def test__contains__containee_inside_container(self):
        # Arrange
        containee = IntRangeInBlock(1, 4)
        container = IntRangeInBlock(0, 6)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertTrue(contained)

    def test__contains__containee_is_container(self):
        # Arrange
        containee = IntRangeInBlock(0, 6)
        container = IntRangeInBlock(0, 6)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertTrue(contained)

    def test__contains__container_inside_containee(self):
        # Arrange
        containee = IntRangeInBlock(0, 6)
        container = IntRangeInBlock(1, 4)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertFalse(contained)

    def test__contains__container_overlaps_containee(self):
        # Arrange
        containee = IntRangeInBlock(0, 3)
        container = IntRangeInBlock(1, 4)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertFalse(contained)

    def test__contains__container_before_containee(self):
        # Arrange
        containee = IntRangeInBlock(3, 6)
        container = IntRangeInBlock(0, 3)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertFalse(contained)

    def test__contains__container_after_containee(self):
        # Arrange
        containee = IntRangeInBlock(0, 3)
        container = IntRangeInBlock(3, 6)

        # Act
        contained = container.contains(containee)

        # Assert
        self.assertFalse(contained)


class DecimalRangeInBlockTest(unittest.TestCase):
    def test__intersection_decimal__overlap(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.3, 2.5)
        range_2 = DecimalRangeInBlock(1.8, 3.0)

        # Act
        overlapping_range = range_1.intersection_decimal(range_2)

        # Assert
        self.assertEqual(overlapping_range, DecimalRangeInBlock(1.8, 2.5))

    def test__intersection_decimal__overlap_within(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.9, 2.5)
        range_2 = DecimalRangeInBlock(1.8, 3.0)

        # Act
        overlapping_range = range_1.intersection_decimal(range_2)

        # Assert
        self.assertEqual(overlapping_range, DecimalRangeInBlock(1.9, 2.5))

    def test__intersection_decimal__no_overlap_before(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.3, 1.5)
        range_2 = DecimalRangeInBlock(1.8, 3.0)

        # Act
        overlapping_range = range_1.intersection_decimal(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__intersection_decimal__no_overlap_after(self):
        # Arrange
        range_1 = DecimalRangeInBlock(3.3, 3.5)
        range_2 = DecimalRangeInBlock(1.8, 3.0)

        # Act
        overlapping_range = range_1.intersection_decimal(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__intersection_int__overlap(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.3, 2.5)
        range_2 = IntRangeInBlock(2, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertEqual(overlapping_range, IntRangeInBlock(2, 3))

    def test__intersection_int__overlap_within(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.9, 2.5)
        range_2 = IntRangeInBlock(1, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertEqual(overlapping_range, IntRangeInBlock(1, 3))

    def test__intersection_int__no_overlap_before(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.3, 1.5)
        range_2 = IntRangeInBlock(2, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__intersection_int__no_overlap_after(self):
        # Arrange
        range_1 = DecimalRangeInBlock(3.3, 3.5)
        range_2 = IntRangeInBlock(1, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__block_nums__positive(self):
        # Arrange
        range_1 = DecimalRangeInBlock(0.5, 3.4)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [0, 1, 2, 3])

    def test__block_nums__negative(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-3.2, -1.4)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [-4, -3, -2])

    def test__block_nums__positive_and_negative(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-5.2, 1.3)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [-6, -5, -4, -3, -2, -1, 0, 1])

    def test__block_nums__positive_and_negative_whole_numbers(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-5.0, 1.0)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [-5, -4, -3, -2, -1, 0])

    def test__to_range_in_block_int__positive_and_negative(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-5.3, 0.5)

        # Act
        int_block_in_range = range_1.to_range_in_block_int()

        # Assert
        self.assertEqual(int_block_in_range, IntRangeInBlock(-6, 1))

    def test__total_block_duration__positive(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 3.4)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertEqual(total_block_duration, 2.2)

    def test__total_block_duration__negative(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-4.6, -1.2)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertAlmostEqual(total_block_duration, 3.4, delta=0.00001)

    def test__total_block_duration__positive_and_negative(self):
        # Arrange
        range_1 = DecimalRangeInBlock(-4.6, 1.2)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertEqual(total_block_duration, 5.8)

    def test__duration_at_step_num__partial_start(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 4.6)
        step_num = 1

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertEqual(duration_at_step_num, 0.8)

    def test__duration_at_step_num__full_start(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.0, 4.6)
        step_num = 1

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertEqual(duration_at_step_num, 1.0)

    def test__duration_at_step_num__full_middle(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 4.6)
        step_num = 2

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertEqual(duration_at_step_num, 1.0)

    def test__duration_at_step_num__partial_end(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 4.6)
        step_num = 4

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertAlmostEqual(duration_at_step_num, 0.6, delta=0.00001)

    def test__duration_at_step_num__full_end(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 5.0)
        step_num = 4

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertEqual(duration_at_step_num, 1.0)

    def test__duration_at_step_num__on_end(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 5.0)
        step_num = 5

        # Act
        duration_at_step_num = range_1.duration_at_step_num(step_num)

        # Assert
        self.assertEqual(duration_at_step_num, 0.0)

    def test__duration_at_step_num__after_range(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 5.0)
        step_num = 6

        # Act / Assert
        with self.assertRaises(RuntimeError):
            range_1.duration_at_step_num(step_num)

    def test__duration_at_step_num__before_range(self):
        # Arrange
        range_1 = DecimalRangeInBlock(1.2, 5.0)
        step_num = 0

        # Act / Assert
        with self.assertRaises(RuntimeError):
            range_1.duration_at_step_num(step_num)

    def test__subtract_decimal__other_is_left(self):
        # Arrange
        other = DecimalRangeInBlock(1.0, 3.0)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertEqual(right, this)
        self.assertIsNone(left)

    def test__subtract_decimal__other_is_right(self):
        # Arrange
        other = DecimalRangeInBlock(5.0, 7.0)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertEqual(left, this)
        self.assertIsNone(right)

    def test__subtract_decimal__other_is_right_overlap(self):
        # Arrange
        other = DecimalRangeInBlock(4.5, 7.0)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertEqual(left, DecimalRangeInBlock(4.0, 4.5))
        self.assertIsNone(right)

    def test__subtract_decimal__other_is_left_overlap(self):
        # Arrange
        other = DecimalRangeInBlock(1.0, 4.2)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertEqual(right, DecimalRangeInBlock(4.2, 5.0))
        self.assertIsNone(left)

    def test__subtract_decimal__other_fully_overlaps(self):
        # Arrange
        other = DecimalRangeInBlock(1.0, 5.0)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertIsNone(right)
        self.assertIsNone(left)

    def test__subtract_decimal__other_intersects(self):
        # Arrange
        other = DecimalRangeInBlock(4.2, 4.4)
        this = DecimalRangeInBlock(4.0, 5.0)

        # Act
        left, right = this.subtract_decimal(other)

        # Assert
        self.assertEqual(left, DecimalRangeInBlock(4.0, 4.2))
        self.assertEqual(right, DecimalRangeInBlock(4.4, 5.0))


class IntRangeInBlockTest(unittest.TestCase):
    def test__intersection_int__overlap(self):
        # Arrange
        range_1 = IntRangeInBlock(1, 3)
        range_2 = IntRangeInBlock(2, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertEqual(overlapping_range, IntRangeInBlock(2, 3))

    def test__intersection_int__overlap_within(self):
        # Arrange
        range_1 = IntRangeInBlock(2, 3)
        range_2 = IntRangeInBlock(1, 4)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertEqual(overlapping_range, IntRangeInBlock(2, 3))

    def test__intersection_int__no_overlap_before(self):
        # Arrange
        range_1 = IntRangeInBlock(0, 1)
        range_2 = IntRangeInBlock(2, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__intersection_int__no_overlap_after(self):
        # Arrange
        range_1 = IntRangeInBlock(3, 4)
        range_2 = IntRangeInBlock(1, 3)

        # Act
        overlapping_range = range_1.intersection_int(range_2)

        # Assert
        self.assertIsNone(overlapping_range)

    def test__block_nums__positive(self):
        # Arrange
        range_1 = IntRangeInBlock(0, 3)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [0, 1, 2])

    def test__block_nums__negative(self):
        # Arrange
        range_1 = IntRangeInBlock(-3, -1)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [-3, -2])

    def test__block_nums__positive_and_negative(self):
        # Arrange
        range_1 = IntRangeInBlock(-5, 1)

        # Act
        block_nums = range_1.block_nums()

        # Assert
        self.assertEqual(list(block_nums), [-5, -4, -3, -2, -1, 0])

    def test__total_block_duration__positive_and_negative(self):
        # Arrange
        range_1 = IntRangeInBlock(-5, 1)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertEqual(total_block_duration, 6)

    def test__total_block_duration__positive(self):
        # Arrange
        range_1 = IntRangeInBlock(1, 3)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertEqual(total_block_duration, 2)

    def test__total_block_duration__negative(self):
        # Arrange
        range_1 = IntRangeInBlock(-4, -1)

        # Act
        total_block_duration = range_1.total_block_duration()

        # Assert
        self.assertEqual(total_block_duration, 3)
