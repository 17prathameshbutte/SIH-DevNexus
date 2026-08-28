import sys
from data.h5_inspector import H5Inspector
import json

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_h5.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    inspector = H5Inspector()
    res = inspector.inspect(filepath)
    print(json.dumps(res, indent=2))
