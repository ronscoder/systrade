
def fixprint(msg, max_char=50):
    print(f'\r{" "*max_char}', end="")
    print(f'\r{msg[:200]}', end="")