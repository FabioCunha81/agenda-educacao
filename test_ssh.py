import paramiko

def test_ssh():
    host = "187.127.45.148"
    user = "root"
    password = "eeX1d3Vnbp#rbN&)"
    
    try:
        print(f"Connecting to {host}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password, timeout=10)
        
        stdin, stdout, stderr = client.exec_command("uptime")
        print("Uptime:", stdout.read().decode())
        
        client.close()
    except Exception as e:
        print("SSH Connection failed:", str(e))

if __name__ == "__main__":
    test_ssh()
