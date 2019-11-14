
def raise_exception(class_name=None, func_name=None, message=None):
  """
    To use
      raise_exception(CLASS.__name__, sys._getframe().f_code.co_name, "MSG")
  """
  raise Exception("class: " + class_name + "\n" +\
      "func_name: " + func_name + "\n" +\
      "message: " + message)

