import inspect
from pal.utilities.math import ddt_filter

# This will print the file path
print(inspect.getfile(ddt_filter))

# This will print the actual source code to your console
print(inspect.getsource(ddt_filter))