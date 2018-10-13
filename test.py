import spur

shell = spur.SshShell(hostname="", username="", password="",missing_host_key=spur.ssh.MissingHostKey.accept)
with shell:
    result = shell.run(["ls"])
print(result.output) # prints hello