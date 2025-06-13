#!/usr/bin/env python3
"""
Simple Remote Control System Launcher
Automatically launches all system components without GUI.
"""

import subprocess
import sys
import os
import time

def launch_component(script_name, title, delay=0):
    """Launch a system component with optional delay."""
    try:
        if delay > 0:
            print(f"⏳ Waiting {delay} seconds before launching {title}...")
            time.sleep(delay)
            
        if not os.path.exists(script_name):
            print(f"❌ Error: {script_name} not found!")
            return False
            
        print(f"🔄 Launching {title}...")
        subprocess.Popen([sys.executable, script_name])
        print(f"✅ {title} launched successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error launching {title}: {str(e)}")
        return False

def main():
    """Launch all components automatically."""
    print("🚀 Remote Control System Auto Launcher")
    print("=" * 50)
    
    # 1. Launch Mediator Server
    print("1️⃣ Starting Mediator Server...")
    if not launch_component("mediator_server.py", "Mediator Server"):
        return
    
    # 2. Launch Login System - First Instance
    print("\n2️⃣ Starting Login System (First Instance)...")
    if not launch_component("login.py", "Login System #1", delay=2):
        return
    
    # 3. Launch Login System - Second Instance
    print("\n3️⃣ Starting Login System (Second Instance)...")
    if not launch_component("login.py", "Login System #2", delay=1):
        return
    
    # 4. Launch Admin Panel
    print("\n4️⃣ Starting Admin Panel...")
    if not launch_component("admin.py", "Admin Panel", delay=2):
        return
    
    print("\n" + "=" * 50)
    print("🎉 All components launched successfully!")
    print("💡 All windows should now be open and ready to use.")
    print("🔚 You can close this window now.")
    
    # Keep script alive for a moment
    input("\nPress Enter to exit launcher...")

if __name__ == "__main__":
    main() 