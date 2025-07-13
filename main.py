import argparse
import logging
import random
import datetime
from faker import Faker
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """Sets up the argument parser for the command-line interface."""
    parser = argparse.ArgumentParser(description="Masks or modifies time-related data while preserving temporal relationships.")

    parser.add_argument("--shift_days", type=int, default=0,
                        help="Shift dates by a random number of days (positive or negative).")
    parser.add_argument("--bucket_interval", type=str, choices=['day', 'week', 'month'],
                        help="Bucket dates into broader time intervals (day, week, month).")
    parser.add_argument("--input_file", type=str,
                        help="Path to the input file containing time-related data.")
    parser.add_argument("--output_file", type=str,
                        help="Path to the output file to write the masked data.")
    parser.add_argument("--date_format", type=str, default="%Y-%m-%d",
                        help="Format of the date in the input file (default: %Y-%m-%d).")
    parser.add_argument("--column_index", type=int, default=0,
                        help="Index of the column containing the date (default: 0).")
    parser.add_argument("--randomize_time", action="store_true", help="Randomize the time portion of a datetime object.")
    return parser

def shift_date(date_str, date_format, shift_days):
    """Shifts a date by a random number of days."""
    try:
        date_object = datetime.datetime.strptime(date_str, date_format)
        random_shift = random.randint(-shift_days, shift_days)
        new_date = date_object + datetime.timedelta(days=random_shift)
        return new_date.strftime(date_format)
    except ValueError as e:
        logging.error(f"Error parsing date: {date_str}. Error: {e}")
        return None # Return None to indicate an error
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def bucket_date(date_str, date_format, bucket_interval):
    """Buckets a date into a broader time interval (day, week, month)."""
    try:
        date_object = datetime.datetime.strptime(date_str, date_format)
        if bucket_interval == 'day':
            return date_object.strftime(date_format)  # No change, already at day level
        elif bucket_interval == 'week':
            start_of_week = date_object - datetime.timedelta(days=date_object.weekday())
            return start_of_week.strftime(date_format)
        elif bucket_interval == 'month':
            return date_object.replace(day=1).strftime(date_format)
        else:
            logging.error(f"Invalid bucket interval: {bucket_interval}")
            return None
    except ValueError as e:
        logging.error(f"Error parsing date: {date_str}. Error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def randomize_time(date_str, date_format):
    """Randomizes the time portion of a datetime object, preserving the date."""
    try:
        date_object = datetime.datetime.strptime(date_str, date_format)
        new_time = datetime.time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        new_datetime = datetime.datetime.combine(date_object.date(), new_time)
        return new_datetime.strftime(date_format)
    except ValueError as e:
        logging.error(f"Error parsing date: {date_str}. Error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
def process_data(input_file, output_file, column_index, date_format, shift_days, bucket_interval, randomize_time_flag):
    """Processes the data in the input file, masks the date, and writes to the output file."""
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    outfile.write("\n")
                    continue # Skip empty lines

                parts = line.split(',') # Assumes comma-separated values.  Modify as needed.
                if len(parts) <= column_index:
                    logging.warning(f"Line does not have enough columns: {line}. Skipping.")
                    outfile.write(line + "\n") # Write original line to output
                    continue
                
                date_str = parts[column_index].strip()

                masked_date = None

                if shift_days > 0:
                    masked_date = shift_date(date_str, date_format, shift_days)
                elif bucket_interval:
                    masked_date = bucket_date(date_str, date_format, bucket_interval)
                elif randomize_time_flag:
                    masked_date = randomize_time(date_str, date_format)
                else:
                    masked_date = date_str  # No masking applied

                if masked_date is None:  # Error occurred during masking
                    logging.warning(f"Failed to mask date in line: {line}. Writing original line to output.")
                    outfile.write(line + "\n")
                    continue
                    
                parts[column_index] = masked_date
                outfile.write(','.join(parts) + '\n')

    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        return 1  # Indicate error
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return 1 # Indicate error
    
    return 0 # Indicate success

def main():
    """Main function to parse arguments and process data."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation:  At least one masking operation must be selected
    if not (args.shift_days > 0 or args.bucket_interval or args.randomize_time):
        parser.error("At least one of --shift_days, --bucket_interval, or --randomize_time must be specified.")
        sys.exit(1)
        
    # Input validation:  Conflicting options: shift_days and bucket_interval are mutually exclusive
    if args.shift_days > 0 and args.bucket_interval:
        parser.error("--shift_days and --bucket_interval are mutually exclusive. Choose only one.")
        sys.exit(1)
        
    if args.input_file and args.output_file:
        result = process_data(args.input_file, args.output_file, args.column_index, args.date_format,
                                args.shift_days, args.bucket_interval, args.randomize_time)
        if result != 0:
            sys.exit(1) # Propagate error to the caller.
        logging.info("Data masking complete.")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

# Example Usage:
# 1. Shift dates by a random number of days (up to 30 days):
#    python main.py --input_file input.csv --output_file output.csv --shift_days 30 --date_format "%Y-%m-%d" --column_index 1
#
# 2. Bucket dates into months:
#    python main.py --input_file input.csv --output_file output.csv --bucket_interval month --date_format "%Y-%m-%d" --column_index 0
#
# 3. Randomize the time portion of datetime objects:
#    python main.py --input_file input.csv --output_file output.csv --randomize_time --date_format "%Y-%m-%d %H:%M:%S" --column_index 2

# Example input.csv:
# id,date,timestamp
# 1,2023-01-15,2023-01-15 10:30:00
# 2,2023-02-20,2023-02-20 14:45:00
# 3,2023-03-10,2023-03-10 08:00:00