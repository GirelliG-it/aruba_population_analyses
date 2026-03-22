import os

def seed_gitkeeps(root_dir="."):
    # Folders we want to make sure exist on GitHub
    target_dirs = [
        'data/raw', 
        'data/processed', 
        'notebooks', 
        'outputs/figures', 
        'outputs/tables', 
        'outputs/exports',
        'scripts',
        'config'
    ]
    
    print(f"--- Seeding .gitkeep files in {os.path.abspath(root_dir)} ---")
    
    for folder in target_dirs:
        # Create the directory if it doesn't exist locally
        os.makedirs(folder, exist_ok=True)
        
        keep_file = os.path.join(folder, ".gitkeep")
        if not os.path.exists(keep_file):
            with open(keep_file, 'w') as f:
                pass  # Create empty file
            print(f"✅ Created: {keep_file}")
        else:
            print(f"ℹ️ Already exists: {keep_file}")

if __name__ == "__main__":
    seed_gitkeeps()
