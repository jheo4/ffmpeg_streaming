import multiprocessing as mp
"""
def test(func, *args):
  print(args[1])
  result = func(*args[0])
  return result


def test_func(a, b):
  c = a + b
  return c

res = test(test_func, [1, 2], 4)
print(res)
"""
import pandas as pd

file = pd.read_csv("test.csv")
print(file.columns)
print(file.values)
print(file.index)
