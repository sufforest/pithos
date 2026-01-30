import sys
import os

# Note: pithos_runner.py sets PYTHONPATH to include 'libs/python' and 'gen/python'
from stringutils import to_upper
from common import user_pb2

def main():
    print("Python Proto Demo")
    
    # 1. Use Shared Library
    original = "hello world"
    upper = to_upper(original)
    print(f"Shared Lib: '{original}' -> '{upper}'")

    # 2. Use Generated Proto
    user = user_pb2.User(name="Pythonista", id=42)
    print(f"Proto Object: {user}")
    print(f"Serialized: {user.SerializeToString()}")

if __name__ == "__main__":
    main()
