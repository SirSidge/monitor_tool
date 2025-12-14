import time

start = time.time()
time.sleep(3)
elapsed = time.time() - start

print(time.ctime(time.time()))

print(f"Elapsed time: {elapsed:.0f}")

path_to_file = "tmp_data.txt"
with open(path_to_file, 'r') as f:
    file_contents = f.read()
    print(file_contents)
with open(path_to_file, 'w') as f:
    f.write("Hello world!")
with open(path_to_file, 'r') as f:
    file_contents = f.read()
    print(file_contents)