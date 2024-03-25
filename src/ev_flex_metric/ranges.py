import math
from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, Tuple, Iterable

DecimalInstantInBlock = float
IntInstantInBlock = int
RangeType = TypeVar("RangeType", bound=float)


@dataclass
class RangeInBlock(Generic[RangeType]):
    start: RangeType
    end: RangeType

    def __init__(self, start: RangeType, end: RangeType):
        self.start = start
        self.end = end
        if start > end:
            raise RuntimeError(f'Cannot create a range where end ({end}) is earlier than start ({start}).')

    def __eq__(self, other) -> bool:
        if isinstance(other, RangeInBlock):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end)

    def overlaps(self, other: 'RangeInBlock') -> bool:
        return not (self.start >= other.end or self.end <= other.start)

    def contains(self, other: 'RangeInBlock') -> bool:
        return self.start <= other.start and self.end >= other.end

    def total_block_duration(self) -> float:
        """Duration of the range in the number of blocks.

        :return: The number of blocks between start and end
        """
        return self.end - self.start


class DecimalRangeInBlock(RangeInBlock[DecimalInstantInBlock]):
    """A range during the block with a start time and an end time. Start is inclusive, end is exclusive."""

    def __init__(self, start: float, end: float):
        super().__init__(start, end)

    def intersection_decimal(self, other: 'RangeInBlock') -> Optional['DecimalRangeInBlock']:
        if self.overlaps(other):
            return DecimalRangeInBlock(max(self.start, other.start), min(self.end, other.end))
        else:
            return None

    def intersection_int(self, other: 'RangeInBlock') -> Optional['IntRangeInBlock']:
        if self.overlaps(other):
            return IntRangeInBlock(math.floor(max(self.start, other.start)), math.ceil(min(self.end, other.end)))
        else:
            return None

    @property
    def start_int(self) -> int:
        return math.floor(self.start)

    @property
    def end_int(self) -> int:
        return math.ceil(self.end)

    def block_nums(self) -> Iterable[int]:
        return iter(range(self.start_int, self.end_int))

    def to_range_in_block_int(self) -> 'IntRangeInBlock':
        return IntRangeInBlock(self.start_int, self.end_int)

    def duration_at_step_num(self, step_num: int) -> float:
        """Duration as a factor of 0..1 of how long the step at step_num is inside the range.

        :param step_num: The absolute step number
        :raise RuntimeError: If step_num is outside of this range.
        :return: Factor of 0..1 denoting that 1 the whole step is inside the range and 0 that none of the
                    step is in the range.
        """
        if step_num < math.floor(self.start) or step_num > math.ceil(self.end):
            raise RuntimeError(f'step_num {step_num} is outside of range {self}')
        start_of_block = max(step_num, self.start)
        end_of_block = min(step_num + 1, self.end)

        return end_of_block - start_of_block

    def subtract_decimal(self, other: 'RangeInBlock') -> Tuple[Optional['DecimalRangeInBlock'],
                                                               Optional['DecimalRangeInBlock']]:
        """Split this range by removing any steps covered by the other range

        :param other: The range to subtract.
        :return: Can return a left and right range. The right range is to the right of the other range. The left
            range is to the left of the other range. If the other range is to the right of this range, it will return
            this range as the left range. If the other range is to the left of this range, it will return this range
            as the right range. It can happen that either left or right is None. It can also happen that both left
            and right are None if the other range fully overlaps this range.
        """
        left = None
        if self.start < other.start:
            left = DecimalRangeInBlock(self.start, min(other.start, self.end))

        right = None
        if self.end > other.end:
            right = DecimalRangeInBlock(max(self.start, other.end), self.end)

        return left, right


class IntRangeInBlock(RangeInBlock[IntInstantInBlock]):
    """A range during the block with a start time and an end time.  Start is inclusive, end is exclusive."""

    def __init__(self, start: int, end: int):
        super().__init__(start, end)

    def intersection_int(self, other: 'IntRangeInBlock') -> Optional['IntRangeInBlock']:
        if self.overlaps(other):
            return IntRangeInBlock(max(self.start, other.start), min(self.end, other.end))
        else:
            return None

    def block_nums(self) -> Iterable[int]:
        return iter(range(self.start, self.end))

    def total_block_duration(self) -> int:
        return int(super().total_block_duration())

    def split_on_int_instant(self, instant: IntInstantInBlock) -> Tuple[Optional['IntRangeInBlock'],
                                                                        Optional['IntRangeInBlock']]:
        if instant > self.end:
            return self, None
        elif instant < self.start:
            return None, self
        else:
            if instant > self.start:
                left = IntRangeInBlock(self.start, instant)
            else:
                left = None

            if instant < self.end:
                right = IntRangeInBlock(instant, self.end)
            else:
                right = None
        return left, right

    def subtract_int(self, other: 'IntRangeInBlock') -> Tuple[Optional['IntRangeInBlock'],
                                                              Optional['IntRangeInBlock']]:
        """Split this range by removing any steps covered by the other range

                :param other: The range to subtract.
                :return: Can return a left and right range. The right range is to the right of the other range. The left
                    range is to the left of the other range. If the other range is to the right of this range, it will return
                    this range as the left range. If the other range is to the left of this range, it will return this range
                    as the right range. It can happen that either left or right is None. It can also happen that both left
                    and right are None if the other range fully overlaps this range.
                """
        left = None
        if self.start < other.start:
            left = IntRangeInBlock(self.start, min(other.start, self.end))

        right = None
        if self.end > other.end:
            right = IntRangeInBlock(max(self.start, other.end), self.end)

        return left, right
