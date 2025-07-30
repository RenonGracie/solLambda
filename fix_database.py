# fix_database_final.py
import os
from sqlalchemy import create_engine, text

# Set the environment variables
os.environ['RDS_HOST'] = 'zaabt5szpidxovz3typgum2iam.dsql.us-east-2.on.aws'
os.environ['RDS_PORT'] = '5432'
os.environ['RDS_DATABASE'] = 'postgres'
os.environ['RDS_USER'] = 'admin'
os.environ['IS_AWS'] = 'true'

from src.db.database import get_db_url

try:
    # Get database URL
    url, args = get_db_url()
    print(f"Connecting to Aurora DSQL database...")
    
    engine = create_engine(url, connect_args=args)
    
    with engine.connect() as conn:
        # Check if payment_type column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signup' 
            AND column_name = 'payment_type'
        """)).fetchone()
        
        if result:
            print("✓ payment_type column exists")
            
            # Update any NULL values to default
            result = conn.execute(text("""
                UPDATE signup 
                SET payment_type = 'out_of_pocket' 
                WHERE payment_type IS NULL
            """))
            conn.commit()
            
            rows_updated = result.rowcount
            print(f"✓ Updated {rows_updated} rows with default value")
            
            print("\n✅ Database is ready!")
        else:
            print("❌ payment_type column not found")
            
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()