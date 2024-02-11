from subprocess import run

user="keeb"
host="keeb.dev"
directory_to_monitor = "/mnt/tmp"
where = "/mnt/nami/media/video/staging"

ssh_cmd = f"ssh {user}@{host} ls {directory_to_monitor}"
print(ssh_cmd)
args = ssh_cmd.split(" ")

yummy = run(args, capture_output=True)
response = yummy.stdout.decode("utf-8").strip()

if response == "":
    print("nothing found, exiting")
    exit(1)

print("files to download:")
print(response)

print("do you want to download everything (y/n)?")
answer = input()
if answer == "y":
    print("downloading")
    scp_cmd = f"scp -r {user}@{host}:{directory_to_monitor}/* {where}"
    print(scp_cmd)
    args = scp_cmd.split(" ")
    run(args)
else:
    print("exiting")
    exit(0)


print("do you want to delete remote files? (y/n)")
delete_cmd = f"ssh {user}@{host} rm -rf \"{directory_to_monitor}/*\""
print(delete_cmd)