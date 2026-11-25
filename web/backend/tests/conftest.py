import os
import sys


BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for module_name in tuple(sys.modules):
    if module_name == "app" or module_name.startswith("app."):
        sys.modules.pop(module_name, None)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
