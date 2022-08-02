import sys
from database import db

def main():
    table_names = sys.argv[1:]

    for table_name in table_names:
        db.table(table_name).truncate()
        print(f"{table_name} table truncated")

if __name__ == "__main__":
    main()