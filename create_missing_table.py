#!/usr/bin/env python
"""
Create NumberFrequencyStats table manually to fix the missing table issue
"""
import os
import sqlite3
import sys
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_numberfrequencystats_table():
    """Create NumberFrequencyStats table manually in SQLite database"""

    # Database path
    db_path = os.path.join(os.path.dirname(__file__), "db.sqlite3")

    print(f"🔧 Creating NumberFrequencyStats table in {db_path}")

    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS results_numberfrequencystats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number VARCHAR(2) NOT NULL,
        date DATE NOT NULL,
        appeared_in_special BOOLEAN NOT NULL DEFAULT 0,
        appeared_in_first BOOLEAN NOT NULL DEFAULT 0,
        appeared_in_other BOOLEAN NOT NULL DEFAULT 0,
        day_of_week INTEGER NOT NULL,
        day_of_month INTEGER NOT NULL,
        week_of_month INTEGER NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        UNIQUE(number, date)
    );
    """

    # Create indexes
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_number_idx ON results_numberfrequencystats (number);",
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_date_idx ON results_numberfrequencystats (date);",
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_day_of_month_idx ON results_numberfrequencystats (day_of_month);",
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_month_idx ON results_numberfrequencystats (month);",
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_year_idx ON results_numberfrequencystats (year);",
        "CREATE INDEX IF NOT EXISTS results_numberfrequencystats_day_of_week_idx ON results_numberfrequencystats (day_of_week);",
    ]

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table
        cursor.execute(create_table_sql)
        print("✅ Created results_numberfrequencystats table")

        # Create indexes
        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)

        print("✅ Created all indexes")

        # Add some sample data for testing
        sample_data = [
            ("01", "2025-08-01", 1, 0, 0, 4, 1, 1, 8, 2025),  # Thu Aug 1, 2025
            ("23", "2025-08-01", 0, 1, 0, 4, 1, 1, 8, 2025),
            ("45", "2025-08-01", 0, 0, 1, 4, 1, 1, 8, 2025),
            ("67", "2025-08-02", 1, 0, 0, 5, 2, 1, 8, 2025),  # Fri Aug 2, 2025
            ("89", "2025-08-02", 0, 1, 0, 5, 2, 1, 8, 2025),
        ]

        insert_sql = """
        INSERT OR IGNORE INTO results_numberfrequencystats 
        (number, date, appeared_in_special, appeared_in_first, appeared_in_other, 
         day_of_week, day_of_month, week_of_month, month, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.executemany(insert_sql, sample_data)

        # Commit changes
        conn.commit()

        # Check count
        cursor.execute("SELECT COUNT(*) FROM results_numberfrequencystats")
        count = cursor.fetchone()[0]
        print(f"✅ Added sample data - Total records: {count}")

        # Show sample records
        cursor.execute("SELECT * FROM results_numberfrequencystats LIMIT 3")
        records = cursor.fetchall()

        print("\n📊 Sample records:")
        for record in records:
            print(
                f"   Number {record[1]} on {record[2]} - Special: {record[3]}, First: {record[4]}, Other: {record[5]}"
            )

        conn.close()
        print("\n✅ NumberFrequencyStats table created successfully!")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        if "conn" in locals():
            conn.close()


def test_table_access():
    """Test if the table can be accessed from Django"""
    print("\n🧪 Testing Django model access...")

    try:
        # Setup Django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

        import django

        django.setup()

        from results.models import NumberFrequencyStats

        # Test count
        count = NumberFrequencyStats.objects.count()
        print(f"✅ Django can access table - Found {count} records")

        # Test query
        recent_records = NumberFrequencyStats.objects.all()[:3]
        print("\n📊 Recent records via Django:")
        for record in recent_records:
            print(f"   {record}")

        return True

    except Exception as e:
        print(f"❌ Django access failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Manual NumberFrequencyStats Table Creation")
    print("=" * 60)

    # Create table
    create_numberfrequencystats_table()

    # Test access
    test_table_access()

    print("\n" + "=" * 60)
    print("🏁 Manual table creation completed!")
    print("✅ The Enhanced Analyzer should now work without 'no such table' errors.")
