from subprocess import run

user="keeb"
host="keeb.dev"
directory_to_monitor = "/home/keeb/Downloads/complete"
empty = "/home/keeb/Downloads/incomplete"

ssh_cmd = f"ssh {user}@{host} ls {directory_to_monitor}"
args = ssh_cmd.split(" ")

yummy = run(args, capture_output=True)

if yummy.stdout == b"":
    exit(1)

