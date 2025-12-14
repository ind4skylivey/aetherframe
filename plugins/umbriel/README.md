# Umbriel - Anti-Analysis Detection Plugin

Detects anti-debugging, anti-VM, anti-instrumentation, and obfuscation techniques in Windows PE binaries.

## Features

- **Anti-Debugging Detection**: `IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, breakpoint detection
- **Anti-VM Detection**: VMware, VirtualBox,QEMU artifacts
- **Anti-Instrumentation**: Frida, PIN, DynamoRIO detection
- **Packing Detection**: UPX, ASPack, PE compression
- **Timing Checks**: RDTSC-based detection
- **Obfuscation**: Control flow flattening, junk code insertion

## Installation

```bash
pip install -e .
```

## Usage

Part of AetherFrame pipeline. Enable in pipeline configuration:

```yaml
plugins:
  - umbriel
```

## Detection Techniques

### Anti-Debugging

- Windows API calls (IsDebuggerPresent, etc.)
- INT 3 breakpoints
- Debug register checks

### Anti-VM

- Registry keys (VMware, VirtualBox)
- Process names (vmtoolsd.exe, vboxservice.exe)
- Hardware identifiers

### Anti-Frida

- Library injection detection
- Thread enumeration
- Memory pattern matching
