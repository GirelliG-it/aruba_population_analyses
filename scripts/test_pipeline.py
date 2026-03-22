import pandas as pd
import os
import sys

def check_project_structure():
    # Define the expected directories based on your tree output
    required_dirs = ['data/raw', 'data/processed', 'outputs/figures', 'scripts']
    
    print("--- Project Structure Verification ---")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Found: {directory}")
        else:
            print(f"❌ Missing: {directory}")
            # We don't exit yet, let's check all of them
            
    # Simple Data Integrity Test
    try:
        df = pd.DataFrame({'test': range(10)})
        test_path = 'data/processed/test_signal.csv'
        df.to_csv(test_path, index=False)
        if os.path.exists(test_path):
            print(f"✅ Write Permissions: Success (Created {test_path})")
            os.remove(test_path) # Clean up
    except Exception as e:
        print(f"❌ Write Permissions: Failed. Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_project_structure()
