from random import randint

def get_confirmation_code():
  code = ""
  random_chars = [randint(0, 9) for _ in range(6)]
  return code.join(str(x) for x in random_chars)