import os

def write_csv(path, file_name, data_points, keys, values):
  target_path = os.path.join(path, file_name)
  keys = keys
  values = values

  data = pd.DataFrame(
        index=data_points,
        colums=keys,
        values
      )
  data.to_csv(output_res, index=False)


if __name__ == "__main__":
  pass
