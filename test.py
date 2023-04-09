import subprocess

stri="worker-node2"
hit = False

for i in map(lambda x: x.split(),subprocess.run(["multipass","list"],stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[1:]):
    try:
        if i[0] == stri:
            hit = True
            break
    except:
        continue

print(hit)