if (-not ("Awake" -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Awake {
    [DllImport("kernel32.dll")]
    public static extern uint SetThreadExecutionState(uint flags);
}
"@
}

$keepAwake = [uint32]::Parse("80000003", [Globalization.NumberStyles]::HexNumber)
$restore   = [uint32]::Parse("80000000", [Globalization.NumberStyles]::HexNumber)

try {
    [void][Awake]::SetThreadExecutionState($keepAwake)
    Write-Host "Display will remain awake. Press Ctrl+C to stop."
    while ($true) {
        Start-Sleep -Seconds 60
    }
}
finally {
    [void][Awake]::SetThreadExecutionState($restore)
}