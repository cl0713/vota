#!/usr/bin/env python3
import subprocess
import serial
import threading
import argparse
import os
import sys
import time

# ───────────────────────── helpers ──────────────────────────
def send_at_command(command: str, ser: serial.Serial) -> None:
    """Send a single AT command followed by CR-LF."""
    print(f"→ {command}")
    ser.write((command + '\r\n').encode())

def read_from_port(ser: serial.Serial) -> None:
    """Continuously display modem responses."""
    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(f"← {line}")
        except Exception as e:
            print(f"[serial] {e}")
            break

def stream_quectel(proc: subprocess.Popen) -> None:
    """Mirror quectel-CM stdout to the console."""
    for byteline in iter(proc.stdout.readline, b''):
        try:
            line = byteline.decode(errors='ignore').rstrip()
        except Exception:
            line = byteline.decode('utf-8', 'replace').rstrip()
        if line:
            print(f"[QC] {line}")

def run_quectel_cm(path: str, apn: str, pin: str, interface: str) -> subprocess.Popen:
    """Launch quectel-CM and pipe its output."""
    path = os.path.expanduser(path)
    return subprocess.Popen(
        ['sudo', path, '-s', apn, '-p', pin, '-i', interface, '-4'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,      # line-buffered
        text=False
    )

# ─────────────────────────── main ───────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Interactive AT console with live quectel-CM output')
    parser.add_argument('--apn', default='oai', help='Access Point Name')
    parser.add_argument('--quectel_cm_path',
                        default='~/quectel_cm/quectel-CM',
                        help='Path to quectel-CM binary')
    parser.add_argument('--pin', default='1111', help='SIM PIN (if required)')
    parser.add_argument('--interface', default='wwan0', help='Network interface')
    parser.add_argument('--port_location', default='/dev/ttyUSB2',
                        help='Serial port for AT commands')
    args = parser.parse_args()

    # ── serial modem ──
    ser = serial.Serial(args.port_location, baudrate=115200, timeout=1)
    send_at_command('AT+CFUN=1', ser)

    threading.Thread(target=read_from_port, args=(ser,), daemon=True).start()
    
    time.sleep(5)

    # ── quectel-CM ──
    qc_proc = run_quectel_cm(args.quectel_cm_path, args.apn, args.pin, args.interface)
    threading.Thread(target=stream_quectel, args=(qc_proc,), daemon=True).start()
    
    time.sleep(2)
    print("Type AT commands: empty line repeats last, 'exit' / 'quit' ends.")

    # ── interactive REPL ──
    last_cmd = ''
    try:
        while True:
            try:
                cmd = input('AT> ').strip()
            except EOFError:          # Ctrl-D
                cmd = 'exit'

            if not cmd:
                cmd = last_cmd

            if cmd.lower() in ('exit', 'quit'):
                break

            send_at_command(cmd, ser)
            last_cmd = cmd
    except KeyboardInterrupt:
        print("\n[info] Ctrl-C received, shutting down…")
    finally:
        try:
            send_at_command('AT+CFUN=0', ser)
        except Exception:
            pass
        ser.close()

        if qc_proc.poll() is None:
            qc_proc.terminate()
            try:
                qc_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                qc_proc.kill()

        print("[info] Goodbye!")

if __name__ == '__main__':
    main()

