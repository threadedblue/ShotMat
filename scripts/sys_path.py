import sys

def print_sys_path():
    """
    Iterates through the directories in sys.path and prints them.
    """
    print("--- Python Module Search Paths (sys.path) ---")
    
    if not sys.path:
        print("sys.path is empty.")
        return

    # Using enumerate to get both the index and the path
    for index, path in enumerate(sys.path):
        print(f"{index}: {path}")
        
    print("---------------------------------------------")

if __name__ == "__main__":
    print_sys_path()
