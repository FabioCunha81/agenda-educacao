import paramiko

def run_command_on_vps(cmd):
    host = "187.127.45.148"
    user = "root"
    password = "eeX1d3Vnbp#rbN&)"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"--- STDOUT ({cmd}) ---")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"--- STDERR ({cmd}) ---")
            print(err)
            
        client.close()
    except Exception as e:
        print("SSH Connection failed:", str(e))

if __name__ == "__main__":
    run_command_on_vps("ls -la /root && ls -la /")
