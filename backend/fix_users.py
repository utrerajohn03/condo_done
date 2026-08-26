import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM users"))
    count = result.scalar()
    print(f"users table has {count} rows")

    if count > 0:
        result = conn.execute(text("SELECT email, role FROM users"))
        for row in result:
            print(f"  {row[0]} ({row[1]})")

    # Drop and let alembic recreate properly
    conn.execute(text("DROP TABLE IF EXISTS condo_unit_residents CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS condo_maintenance_requests CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS condo_units CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS organizations CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS condo_alembic_version"))
    conn.commit()
    print("Dropped all tables. Re-running alembic...")
