import os
import pandas as pd

def write_csv(path, file_name, data_points, columns, values):
  target_path = os.path.join(path, file_name)

  data = pd.DataFrame(
        values,
        index=data_points,
        columns=columns
      )
  data.to_csv(target_path)


def read_csv(path, file_name):
  target_path = os.path.join(path, file_name)
  file = pd.read_csv(target_path, index_col=0)

  data_points = file.index
  columns = file.columns
  values = file.values

  return data_points, columns, values


if __name__ == "__main__":
  dir = os.environ['REPO_HOME']
  write_csv(dir, 'test.csv', [0, 1, 2, 3, 4], ['a', 'b', 'c', 'd'],
      [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16],
        [17, 18, 19, 20]])
  dps, columns, values = read_csv(dir, 'test.csv')

  print(dps)
  print(columns)
  print(values)

