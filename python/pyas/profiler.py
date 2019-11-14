import os
import psutil
import multiprocessing as mp
import numpy as np


class Profiler():
  __instance = None


  @staticmethod
  def get_instance():
    if Profiler.__instance is None:
      Profiler.__instance = Profiler()
    return Profiler.__instance


  def execute(self, *args):
    target_function = args[0]
    params = args[1][0]
    pipe_end = args[2]
    result = target_function(*params)
    pipe_end.send(result)


  def profile_cpu(self, freq, target_function, *args):
    data_points = []
    columns = []
    values = []
    interval = 1/freq

    for i in range(mp.cpu_count()):
      columns.append("cpu (" + str(i) + ")")

    recv_end, send_end = mp.Pipe(False)
    exe_context = []
    exe_context.append(target_function)
    exe_context.append(args)
    exe_context.append(send_end)

    for i in range(30):  # warm up 3sec
      values.append(psutil.cpu_percent(interval, percpu=True))

    target_process = mp.Process(target=self.execute, args=exe_context)
    target_process.start()
    psutil_process = psutil.Process(target_process.pid)

    while target_process.is_alive():
      values.append(psutil.cpu_percent(interval, percpu=True))
    target_process.join()

    for i in range(30):  # wrap up 3sec
      values.append(psutil.cpu_percent(interval, percpu=True))
    for i in range(len(values)):
      data_points.append(str(round(i * interval, 2)) + "s")

    target_result = recv_end.recv()

    return target_result, data_points, columns, values


if __name__ == "__main__":
  def test_func(a, b, c):
    result = []
    for i in range(50000):
      result.append(a + b + c + i)
    return result

  profiler = Profiler.get_instance()
  res, dps, columns, values = profiler.profile_cpu(100, test_func, [1, 2, 3])
  print(dps, columns, values)

