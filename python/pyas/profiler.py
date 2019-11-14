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

    print(target_function)
    print(params[0])
    print(pipe_end)

    print("executes the target function...")
    result = target_function(*params)
    pipe_end.send(result)
    print("end execution...")


  def profile_cpu(self, target_function, *args):
    data_points = []
    colum_keys = []
    values = []
    for i in range(mp.cpu_count()):
      colum_keys.append("cpu (" + str(i) + ")")

    recv_end, send_end = mp.Pipe(False)
    exe_context = []
    exe_context.append(target_function)
    exe_context.append(args)
    exe_context.append(send_end)

    for i in range(30):  # warm up 3sec
      values.append(psutil.cpu_percent(interval=0.1, percpu=True))

    target_process = mp.Process(target=self.execute, args=exe_context)
    target_process.start()
    psutil_process = psutil.Process(target_process.pid)

    while target_process.is_alive():
      values.append(psutil.cpu_percent(interval=0.1, percpu=True))
    target_process.join()

    for i in range(30):  # wrap up 3sec
      values.append(psutil.cpu_percent(interval=0.1, percpu=True))
    for i in range(len(values)):
      data_points.append(str(round(i * 0.1, 1)) + "s")

    target_result = recv_end.recv()

    return target_result, data_points, colum_keys, values


if __name__ == "__main__":
  def test_func(a, b, c):
    result = []
    for i in range(10):
      result.append(a + b + c + i)
    return result

  profiler = Profiler.get_instance()
  res, dps, keys, values = profiler.profile_cpu(test_func, [1, 2, 3])
  print(res)
  print(dps, keys, values)

