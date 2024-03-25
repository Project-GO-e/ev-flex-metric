import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import reduce
from itertools import combinations
from pathlib import Path
from typing import List

import pandas
import pytz
from dataclass_binder import Binder

from ev_flex_metric.main import ChargingSession, EnergyProfile, BlockMetadata
from ev_flex_metric.ranges import DecimalRangeInBlock, IntRangeInBlock


def write_df_to_file(config: 'OutputProfilesConfig', filename: str, df: pandas.DataFrame) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    match config.file_format_enum:
        case OutputFileFormat.CSV:
            df.to_csv(config.output_dir / f'{filename}.csv',
                      sep=config.csv_seperator,
                      header=config.csv_include_headerline,
                      decimal=config.csv_decimal_sign)
        case OutputFileFormat.PARQUET:
            df = df.rename(str, axis='columns')
            df.to_parquet(config.output_dir / f'{filename}.parquet')
        case _:
            raise RuntimeError(f'Unknown extension {config.file_format}')


def shift_energy_profile_for_charger(profile_range: IntRangeInBlock,
                                     flex_window: BlockMetadata,
                                     congestion: IntRangeInBlock,
                                     charge_sessions: list[ChargingSession]) -> EnergyProfile:
    """Create the shifted energy profile for a given charger.

    :param profile_range: The range in time for which the energy profile should be generated.
    :param congestion: When congestion occurs.
    :param charge_sessions: The charge sessions of the charger which happen during profile_range.
    :return: An energy profile where all charge sessions are added to after shifting them according to congestion.
    """
    result_energy_profile = EnergyProfile(profile_range, [0.0] * profile_range.total_block_duration())

    for charge_session in charge_sessions:
        shifted_energy_profile = charge_session.shift_flexible_energy_after_congestion(flex_window, congestion)
        outside_of_result_profile_left, outside_of_result_profile_right = shifted_energy_profile.split_on_int(result_energy_profile.range_in_block)

        outside_ranges = []
        if outside_of_result_profile_left is not None:
            outside_ranges.append(outside_of_result_profile_left.range_in_block)
        if outside_of_result_profile_right is not None:
            outside_ranges.append(outside_of_result_profile_right.range_in_block)

        if outside_ranges:
            raise RuntimeError(f'Charge session {charge_session} shifted energy to '
                               f'{shifted_energy_profile.range_in_block} which was outside of result profile '
                               f'{result_energy_profile.range_in_block} on ranges {outside_ranges}')
        result_energy_profile = result_energy_profile.profile_addition(shifted_energy_profile)

    return result_energy_profile


def generate_charging_sessions_from_charger_energy_profile(charge_session_ranges: list[DecimalRangeInBlock],
                                                           max_charging_power_watt_per_charging_session: list[float],
                                                           charger_energy_profile: EnergyProfile,
                                                           meta_data: BlockMetadata) -> list[ChargingSession]:
    """Generate the charging sessions from a common charger energy profile.

    For each charging session, the portion of the charger energy profile is selected that corresponds with the
    beginning and end of the charging session.

    Assumption: No charging sessions overlap in time.
    Assumption: The charging session list is complete and explains the energy profile.
    If any of these assumptions do not hold, a RuntimeError is raised.

    :param charge_session_ranges: All charge sessions in charger_energy_profile.
        Expect in the same order as max_charging_power_watt_per_charging_session.
    :param max_charging_power_watt_per_charging_session: The maximum charging power per charge session.
        Expect in the same order as charge_session_ranges.
    :param charger_energy_profile:
    :param meta_data: The time window in which we are considering charging sessions.
    :return: List of charging sessions that result in the charger_energy_profile.
    """
    for charge_session_range_1, charge_session_range_2 in combinations(charge_session_ranges, 2):
        if charge_session_range_1.overlaps(charge_session_range_2):
            raise RuntimeError(f'Two charge session ranges overlap and so cannot divide the energy profile evenly. '
                               f'Charge session 1: {charge_session_range_1}, charge session '
                               f'2: {charge_session_range_2}')

    charge_sessions = []
    result_energy_profile = EnergyProfile(charger_energy_profile.range_in_block,
                                          [0.0] * charger_energy_profile.range_in_block.total_block_duration())
    for charge_session_range, max_charging_power_watt in zip(charge_session_ranges,
                                                             max_charging_power_watt_per_charging_session):
        charge_session_energy_profile = charger_energy_profile.mask_decimal(charge_session_range)
        result_energy_profile = result_energy_profile.profile_addition(charge_session_energy_profile)
        charge_sessions.append(ChargingSession(charge_session_range,
                                               max_charging_power_watt,
                                               charge_session_energy_profile,
                                               meta_data))

    if result_energy_profile != charger_energy_profile:
        raise RuntimeError(f'Resulting energy profile for all charge sessions ({result_energy_profile}) do not equal '
                           f'to the energy profile of the charger ({charger_energy_profile}).')

    return charge_sessions


@dataclass
class InputConfig:
    charge_sessions_path_parquet: Path
    energy_profiles_path_template_parquet: str


class OutputFileFormat(Enum):
    PARQUET = 'parquet'
    CSV = 'csv'


@dataclass
class OutputProfilesConfig:
    file_format: str
    output_dir: Path
    csv_include_headerline: bool = True
    csv_decimal_sign: str = '.'
    csv_seperator: str = ';'

    @property
    def file_format_enum(self) -> OutputFileFormat:
        match self.file_format.lower():
            case 'csv':
                return OutputFileFormat.CSV
            case 'parquet':
                return OutputFileFormat.PARQUET
            case _:
                raise RuntimeError(f'Unknown extension {self.file_format}')


@dataclass
class OutputConfig:
    profile_start: datetime
    profile_end: datetime
    baseline_profiles: OutputProfilesConfig
    shifted_profiles: OutputProfilesConfig


@dataclass
class CongestionStartIterateConfig:
    first_congestion_start: datetime
    congestion_start_until: datetime
    next_congestion_after: timedelta


@dataclass
class Config:
    pc4: int
    congestion_durations_ptu: List[int]
    flex_window_start_before_congestion_start_ptu: int
    flex_window_durations_ptu: List[int]
    input: InputConfig
    output: OutputConfig
    ptu_duration: timedelta = timedelta(minutes=15)
    congestion_start_moments: list[datetime] | None = None
    congestion_starts_iterate_until: CongestionStartIterateConfig | None = None

    def congestion_starts(self) -> list[datetime]:
        if self.congestion_start_moments:
            result = self.congestion_start_moments
        elif self.congestion_starts_iterate_until:
            result = []
            current_congestion_start = self.congestion_starts_iterate_until.first_congestion_start
            last_congestion_start = self.congestion_starts_iterate_until.congestion_start_until
            while current_congestion_start < last_congestion_start:
                result.append(current_congestion_start)
                current_congestion_start = current_congestion_start + self.congestion_starts_iterate_until.next_congestion_after
        else:
            raise RuntimeError('Either the table "congestion_starts_iterate_until" or the field "congestion_starts" '
                               'must be set. Currently they are both missing.')

        return result


def main():
    try:
        config_path = Path(os.environ.get("CONFIG_PATH", "config.toml"))
        print(f"Reading config path at {config_path}")
        config = Binder(Config).parse_toml(config_path)
    except Exception as ex:
        print(f"Error reading configuration file: {ex}")
        sys.exit(1)

    df_index = pandas.date_range(config.output.profile_start.replace(tzinfo=None),
                                 config.output.profile_end.replace(tzinfo=None),
                                 freq=config.ptu_duration,
                                 inclusive='left')

    print('Reading in charge sessions...')
    df_charge_sessions = pandas.read_parquet(config.input.charge_sessions_path_parquet)
    print('Read in charge sessions!')

    df_charge_sessions = df_charge_sessions[(df_charge_sessions['pc4'] == config.pc4)]
    congestion_starts = config.congestion_starts()

    for (pc4,), df_charge_sessions_pc4_group in df_charge_sessions.groupby(by=['pc4']):
        print(f'Reading in energy profiles for pc4 area {pc4}...')
        df_energy_profiles_for_pc4 = pandas.read_parquet(config.input.energy_profiles_path_template_parquet.replace('{pc4}', str(pc4)))
        df_energy_profiles_for_pc4['time'] = df_energy_profiles_for_pc4['time'].dt.tz_localize(pytz.utc)
        print(f'Read in energy profiles!')

        pc4_charge_sessions_grouped_by_household = df_charge_sessions_pc4_group.groupby(by=['household_id'])
        for flex_window_duration in config.flex_window_durations_ptu:
            for congestion_duration in config.congestion_durations_ptu:
                for congestion_start in congestion_starts:
                    current_congestion_end = congestion_start + (config.ptu_duration * congestion_duration)
                    flex_window_start = congestion_start - timedelta(seconds=config.flex_window_start_before_congestion_start_ptu * config.ptu_duration.total_seconds())
                    flex_window_end = flex_window_start + timedelta(seconds=flex_window_duration * config.ptu_duration.total_seconds())
                    flex_window = BlockMetadata(flex_window_start,
                                                flex_window_end,
                                                config.ptu_duration)
                    print(f'Processing pc4: {pc4} flexwindow_start: {flex_window_start} flexwindow_end: {flex_window_end} (duration: {flex_window_duration}) congestion_start: {congestion_start}, congestion_end: {current_congestion_end} (duration: {congestion_duration}) for {len(pc4_charge_sessions_grouped_by_household)} households')

                    congestion = flex_window.convert_to_range_in_block_int(congestion_start,
                                                                           current_congestion_end)

                    if congestion.subtract_int(flex_window.to_range_in_block_int()) != (None, None):
                        raise RuntimeError(f'Congestion({congestion}) should be fully within flex_window!')

                    zero_energy_profile_range = flex_window.convert_to_range_in_block_int(config.output.profile_start,
                                                                                          config.output.profile_end)
                    zero_energy_profile = EnergyProfile(zero_energy_profile_range,
                                                        [0.0] * zero_energy_profile_range.total_block_duration())
                    df_shifted_profiles_data = {}
                    df_baselines_profiles_data = {}
                    for (household_id,), df_charge_sessions_household_group in pc4_charge_sessions_grouped_by_household:
                        charge_sessions_on_charger = []
                        for _, df_charge_session in df_charge_sessions_household_group.iterrows():
                            session_start = df_charge_session['startTime'].replace(tzinfo=pytz.utc)
                            session_end = df_charge_session['plugOutTime'].replace(tzinfo=pytz.utc)

                            kwatt_profile_series_charging_session: pandas.Series = df_energy_profiles_for_pc4[str(df_charge_session['session_id'])]
                            kwatt_profile_series_charging_session.index = df_energy_profiles_for_pc4['time']
                            session_dec = flex_window.convert_to_range_in_block_decimal(session_start,
                                                                                           session_end)
                            session_int = session_dec.to_range_in_block_int()
                            normalized_session_start, normalized_session_end = flex_window.from_int_block(session_int)
                            kwatt_profile_series_charging_session = kwatt_profile_series_charging_session[(kwatt_profile_series_charging_session.index >= normalized_session_start) & (kwatt_profile_series_charging_session.index < normalized_session_end)]

                            energy_profile_series_charging_session = kwatt_profile_series_charging_session * 1000 * config.ptu_duration.total_seconds()
                            charge_session = ChargingSession(session=session_dec,
                                                             max_charging_power_watt=df_charge_session['maxChargePower_kW'] * 1000,
                                                             energy_to_charge_profile=EnergyProfile(range_in_block=session_int,
                                                                                                    energy_per_block=energy_profile_series_charging_session.values.tolist()),
                                                             meta_data=flex_window,
                                                             fix_energy_profile=True)
                            charge_sessions_on_charger.append(charge_session)

                        shifted_energy_profile_household = shift_energy_profile_for_charger(profile_range=zero_energy_profile.range_in_block,
                                                                                            flex_window=flex_window,
                                                                                            congestion=congestion,
                                                                                            charge_sessions=charge_sessions_on_charger)

                        shifted_profile_household_series = pandas.Series(data=shifted_energy_profile_household.value_per_block,
                                                                         index=df_index)
                        watt_shifted_profile_household_series = shifted_profile_household_series / config.ptu_duration.total_seconds()
                        df_shifted_profiles_data[household_id] = watt_shifted_profile_household_series

                        baseline_energy_profile = reduce(lambda baseline, cs: baseline.profile_addition(cs.energy_to_charge_profile),
                                                         charge_sessions_on_charger,
                                                         zero_energy_profile)
                        baseline_profile_household_series = pandas.Series(data=baseline_energy_profile.value_per_block,
                                                                          index=df_index)
                        watt_baseline_profile_household_series = baseline_profile_household_series / config.ptu_duration.total_seconds()
                        df_baselines_profiles_data[household_id] = watt_baseline_profile_household_series

                    df_baseline_profiles = pandas.DataFrame(data=df_baselines_profiles_data, index=df_index)
                    df_shifted_profiles = pandas.DataFrame(data=df_shifted_profiles_data, index=df_index)
                    flex_window_start_str = flex_window_start.replace(tzinfo=None) \
                                                             .isoformat(timespec="minutes") \
                                                             .replace(":", "")
                    congestion_start_str = congestion_start.replace(tzinfo=None)\
                                                           .isoformat(timespec="minutes")\
                                                           .replace(":", "")
                    filename = f'pc4{pc4}_flexwindowstart{flex_window_start_str}_flexwindowduration{flex_window_duration}_congestionstart{congestion_start_str}_congestionduration{congestion_duration}'
                    write_df_to_file(config.output.baseline_profiles, filename, df_baseline_profiles)
                    write_df_to_file(config.output.shifted_profiles, filename, df_shifted_profiles)


if __name__ == '__main__':
    main()
