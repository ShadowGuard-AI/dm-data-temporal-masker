# dm-data-temporal-masker
Masks or modifies time-related data, such as timestamps or date ranges, while preserving temporal relationships (e.g., order of events, durations). Can shift time values by a random offset or bucket them into broader time intervals (e.g., days, weeks, months) while ensuring consistency across related records. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowGuardAI/dm-data-temporal-masker`

## Usage
`./dm-data-temporal-masker [params]`

## Parameters
- `-h`: Show help message and exit
- `--shift_days`: No description provided
- `--bucket_interval`: No description provided
- `--input_file`: Path to the input file containing time-related data.
- `--output_file`: Path to the output file to write the masked data.
- `--date_format`: No description provided
- `--column_index`: No description provided
- `--randomize_time`: Randomize the time portion of a datetime object.

## License
Copyright (c) ShadowGuardAI
