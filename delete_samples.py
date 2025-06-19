import pandas as pd
import sqlite3
import pathlib
import sys

from db_manager.db_deletion import delete_sample

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print("Need samples to delete, exiting.")
        sys.exit(0)

    dest_path = pathlib.Path("cell_count.db")
    conn = sqlite3.connect(dest_path)
    for sample in sys.argv[1:]:
        print(f"Deleting {sample}.")
        delete_sample(conn, sample)
