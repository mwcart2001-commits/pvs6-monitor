import sqlite3
import csv
import argparse
from datetime import datetime

DB_PATH = "/home/pi/pvs6-monitor/pvs6_data.db"

def export_to_csv(start_date, end_date, output_file, table):
    # Convert YYYY-MM-DD → Unix timestamps
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = f"""
        SELECT *
        FROM {table}
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    """

    cursor.execute(query, (start_ts, end_ts))
    rows = cursor.fetchall()

    # Column names
    col_names = [description[0] for description in cursor.description]

    # Write CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(rows)

    conn.close()

    print(f"Export complete. {len(rows)} rows saved to {output_file}")


def parse_args():
    parser = argparse.ArgumentParser(description="Export PVS6 data to CSV for a date range.")

    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--table", required=True, help="Table name (system_data or panel_data)")
    parser.add_argument("--out", required=True, help="Output CSV filename")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_to_csv(args.start, args.end, args.out, args.table)
