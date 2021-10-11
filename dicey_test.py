import os

tests = os.listdir('./tests')
for test in tests:
    file_path = './tests/'+test
    os.system(f'dicey {file_path}')
