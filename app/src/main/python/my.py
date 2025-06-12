import io
import sys

def say_hello():
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    # print("这是 print 的输出")
    print("Test Python")

    sys.stdout = old_stdout
    return buffer.getvalue()