import paramiko

def run_command_on_vps(cmd):
    hosts = ["107.127.45.148", "187.127.45.148"]
    user = "root"
    password = "eeX1d3Vnbp#rbN&)"
    
    for host in hosts:
        print(f"Trying host {host}...")
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, username=user, password=password, timeout=10)
            
            stdin, stdout, stderr = client.exec_command(cmd)
            print(f"--- STDOUT ({cmd}) on {host} ---")
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"--- STDERR ({cmd}) on {host} ---")
                print(err)
                
            client.close()
            return # success
        except Exception as e:
            print(f"SSH Connection failed for {host}:", str(e))

if __name__ == "__main__":
    run_command_on_vps("uptime")
