<style>
/* Enable text wrapping in code blocks */
code {
  white-space : pre-wrap !important;
}
</style>

# Tiger VNC Server Setup

## Introduction

This article explains the process I used to leverage Perplexity and Anthropic to create a script to install and configure Tiger VNC Server on Pop!_OS 20.04.


## Process

### Perplexity

#### Research

##### FINDING THE RIGHT TOOLS

###### Prompt

> What are the best remote desktop server options for using my pop os computer while I'm away?

###### Response

````markdown 
Based on the search results and your specific query about remote desktop server options for Pop!_OS, here are some of the best options:

## NoMachine

NoMachine appears to be one of the top recommendations:

- It's free for personal use and works across Windows, macOS, and Linux.
- Installation is quick and straightforward on Pop!_OS.
- Offers high performance and a seamless remote desktop experience.
- Setup process is simple - just install the software and it's ready to accept connections[4].

## xRDP

While it requires more setup, xRDP is a solid option for enabling remote desktop on Pop!_OS:

- It's based on the RDP protocol, making it compatible with Windows Remote Desktop clients.
- Requires installation and configuration on your Pop!_OS machine.
- Allows for a native-like remote desktop experience[3].

## TigerVNC

TigerVNC is a robust VNC server option:

- It's free and open-source.
- Provides high performance, especially for 3D/Video data over remote connections.
- Offers both client and server packages[2].

## X2Go

X2Go is another Linux-based remote desktop server option:

- Based on NX technology developed by NoMachine.
- Includes both client and server packages.
- Available for Linux, Windows, and macOS[2].

When setting up a remote desktop server on your Pop!_OS computer, consider factors such as ease of setup, performance, security features, and compatibility with the devices you'll be using to connect remotely. NoMachine stands out as a particularly good option for Pop!_OS users due to its ease of use and cross-platform compatibility. However, xRDP, TigerVNC, and X2Go are also solid choices, especially if you prefer open-source solutions.

Remember to secure your remote desktop server properly, regardless of which option you choose. This includes using strong passwords, enabling encryption, and configuring firewalls appropriately.

Citations:
[1] https://www.tecmint.com/best-linux-rdp-remote-desktop-clients/
[2] https://www.debugpoint.com/best-remote-desktop-clients-ubuntu/
[3] https://c-nergy.be/blog/?p=16637
[4] https://www.youtube.com/watch?v=iNZjB8vvOAw
[5] https://snapcraft.io/install/remmina/pop
[6] https://www.techradar.com/best/best-linux-remote-desktop-clients
[7] https://www.cendio.com/blog/10-best-remote-desktop-software-tools-for-linux-users/
[8] https://support.system76.com/articles/desktop-environment/
````

##### FINDING THE INSTALLATION PROCESS

###### A Quick Web Search

No prompt here, just a search for `tigervnc server install linux`

A quick scan of the results landed me here: https://www.cyberciti.biz/faq/install-and-configure-tigervnc-server-on-ubuntu-18-04/

Seems like a fair resource to start with.

###### Prompt: Give me the steps to install and configure TigerVNC server

> site:https://www.cyberciti.biz/faq/install-and-configure-tigervnc-server-on-ubuntu-18-04/ 
>
> Give me step by step

###### Response

````markdown
Based on the search results, here are step-by-step instructions for installing and configuring TigerVNC server on Ubuntu:

1. Update the system:
```
sudo apt update
sudo apt upgrade
```

2. Install TigerVNC server and required packages:
```
sudo apt install tigervnc-standalone-server tigervnc-common
```

3. Start the VNC server for initial configuration:
```
vncserver
```
   - Set a VNC password when prompted

4. Stop the VNC server:
```
vncserver -kill :1
```

5. Create a VNC startup script:
```
nano ~/.vnc/xstartup
```

6. Add the following content to the xstartup file:
```
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startxfce4
```

7. Make the xstartup file executable:
```
chmod u+x ~/.vnc/xstartup
```

8. Start the VNC server again:
```
vncserver
```

9. To connect securely, create an SSH tunnel from your local machine:
```
ssh -L 5901:127.0.0.1:5901 -C -N -l username your_server_ip
```

10. Use a VNC viewer on your local machine to connect to localhost:5901

11. (Optional) To set up VNC as a systemd service, create a unit file:
```
sudo nano /etc/systemd/system/vncserver@.service
```
   - Add the appropriate configuration (refer to the full guide for details)

12. Enable and start the VNC service:
```
sudo systemctl enable vncserver@1
sudo systemctl start vncserver@1
```

These steps should get TigerVNC server running on your Ubuntu system. Remember to secure your VNC setup by using SSH tunneling and strong passwords.

Citations:
[1] https://community.hetzner.com/tutorials/install-tigervnc/
[2] https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04
[3] https://linuxize.com/post/how-to-install-and-configure-vnc-on-ubuntu-18-04/
[4] https://www.tecmint.com/install-and-configure-vnc-server-on-ubuntu/
[5] https://www.tecmint.com/best-linux-rdp-remote-desktop-clients/
[6] https://www.youtube.com/watch?v=iNZjB8vvOAw
[7] https://github.com/TigerVNC/tigervnc/issues/794
[8] https://www.techradar.com/best/best-linux-remote-desktop-clients
````

### Anthropic

#### Implementation

##### COMPILING THE STEPS INTO A SCRIPT

###### Prompt: Create a script to install and configure TigerVNC server

> Write a BASH script to help my achieve the following steps.
>
> ... <Copy and paste the steps from the Perplexity response> ...

> NOTE: I'm leaving in the typo from the original prompt to show the flexibility of the LLM in understanding the user's intent.

###### Response

````markdown
Certainly! I'll create a Bash script that automates the process of installing and configuring TigerVNC server on Ubuntu. Here's the script:

```bash
#!/bin/bash

# Function to check if a command was successful
check_command() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Update the system
echo "Updating the system..."
sudo apt update && sudo apt upgrade -y
check_command "Failed to update the system"

# Install TigerVNC server and required packages
echo "Installing TigerVNC server and required packages..."
sudo apt install -y tigervnc-standalone-server tigervnc-common
check_command "Failed to install TigerVNC server"

# Set VNC password
echo "Setting VNC password..."
vncpasswd
check_command "Failed to set VNC password"

# Create VNC startup script
echo "Creating VNC startup script..."
cat > ~/.vnc/xstartup << EOL
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startxfce4
EOL
check_command "Failed to create VNC startup script"

# Make the xstartup file executable
chmod u+x ~/.vnc/xstartup
check_command "Failed to make xstartup file executable"

# Create systemd service file
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/vncserver@.service > /dev/null << EOL
[Unit]
Description=Start TigerVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=/home/$USER

PIDFile=/home/$USER/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1280x800 :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
EOL
check_command "Failed to create systemd service file"

# Enable and start the VNC service
echo "Enabling and starting VNC service..."
sudo systemctl daemon-reload
sudo systemctl enable vncserver@1.service
sudo systemctl start vncserver@1.service
check_command "Failed to enable and start VNC service"

echo "TigerVNC server installation and configuration completed successfully!"
echo "To connect securely, create an SSH tunnel from your local machine:"
echo "ssh -L 5901:127.0.0.1:5901 -C -N -l $USER $(hostname -I | awk '{print $1}')"
echo "Then use a VNC viewer on your local machine to connect to localhost:5901"

```

This script automates the process of installing and configuring TigerVNC server on Ubuntu. Here's a breakdown of what the script does:

1. Updates the system
2. Installs TigerVNC server and required packages
3. Prompts the user to set a VNC password
4. Creates and configures the VNC startup script
5. Sets up TigerVNC as a systemd service
6. Enables and starts the VNC service

To use this script:

1. Save it to a file, for example, `install_tigervnc.sh`
2. Make the script executable: `chmod +x install_tigervnc.sh`
3. Run the script: `./install_tigervnc.sh`

The script will prompt you to enter your sudo password when necessary and to set a VNC password.

After running the script, you can connect to your VNC server securely by creating an SSH tunnel from your local machine, as mentioned in the script's output.

Note: This script assumes you're using Xfce as your desktop environment. If you're using a different desktop environment, you'll need to modify the `xstartup` file content accordingly.

Would you like me to explain any part of the script in more detail?
````

This script automates the process of installing and configuring TigerVNC server on Ubuntu using Xcfe as the desktop environment. However, I'm using Pop!_OS 20.04, which uses GNOME as the default desktop environment.

###### Prompt: Create a script to install and configure TigerVNC server (Follow-up)

> Will this script work for installation on Pop!_OS?

````markdown
Pop!_OS is based on Ubuntu, so this script should work on Pop!_OS with a few minor considerations. Let's discuss the compatibility:

1. Package Management: Pop!_OS uses the same APT package manager as Ubuntu, so the package installation commands should work without modification.

2. Desktop Environment: Pop!_OS uses GNOME as its default desktop environment, not Xfce. We'll need to adjust the script for this.

3. System Services: Pop!_OS uses systemd, just like Ubuntu, so the service configuration should work as-is.

Given these points, I'll modify the script to make it more compatible with Pop!_OS. Here's the updated version:



```bash
#!/bin/bash

# Function to check if a command was successful
check_command() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Update the system
echo "Updating the system..."
sudo apt update && sudo apt upgrade -y
check_command "Failed to update the system"

# Install TigerVNC server and required packages
echo "Installing TigerVNC server and required packages..."
sudo apt install -y tigervnc-standalone-server tigervnc-common
check_command "Failed to install TigerVNC server"

# Set VNC password
echo "Setting VNC password..."
vncpasswd
check_command "Failed to set VNC password"

# Create VNC startup script
echo "Creating VNC startup script..."
cat > ~/.vnc/xstartup << EOL
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export XKL_XMODMAP_DISABLE=1
export XDG_CURRENT_DESKTOP="GNOME-Flashback:GNOME"
export XDG_MENU_PREFIX="gnome-flashback-"
gnome-session --session=gnome-flashback-metacity --disable-acceleration-check &
EOL
check_command "Failed to create VNC startup script"

# Make the xstartup file executable
chmod u+x ~/.vnc/xstartup
check_command "Failed to make xstartup file executable"

# Create systemd service file
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/vncserver@.service > /dev/null << EOL
[Unit]
Description=Start TigerVNC server at startup
After=syslog.target network.target

[Service]
Type=forking
User=$USER
Group=$USER
WorkingDirectory=/home/$USER

PIDFile=/home/$USER/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry 1920x1080 :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
EOL
check_command "Failed to create systemd service file"

# Enable and start the VNC service
echo "Enabling and starting VNC service..."
sudo systemctl daemon-reload
sudo systemctl enable vncserver@1.service
sudo systemctl start vncserver@1.service
check_command "Failed to enable and start VNC service"

echo "TigerVNC server installation and configuration completed successfully!"
echo "To connect securely, create an SSH tunnel from your local machine:"
echo "ssh -L 5901:127.0.0.1:5901 -C -N -l $USER $(hostname -I | awk '{print $1}')"
echo "Then use a VNC viewer on your local machine to connect to localhost:5901"
```

Key changes made for Pop!_OS compatibility:

1. The `xstartup` script has been modified to use GNOME Flashback session instead of Xfce. This provides a lighter-weight GNOME experience that works well with VNC.

2. The screen resolution in the systemd service file has been increased to 1920x1080, which is more common for modern displays.

3. Everything else remains largely the same, as Pop!_OS uses the same package manager and systemd as Ubuntu.

To use this script on Pop!_OS:

1. Save it to a file, for example, `install_tigervnc_pop.sh`
2. Make the script executable: `chmod +x install_tigervnc_pop.sh`
3. Run the script: `./install_tigervnc_pop.sh`

The script will prompt you to enter your sudo password when necessary and to set a VNC password.

After running the script, you can connect to your VNC server securely by creating an SSH tunnel from your local machine, as mentioned in the script's output.

Note: If you encounter any issues with the GNOME session, you might need to install the GNOME Flashback session:

```bash
sudo apt install gnome-session-flashback
```

This script should work well on Pop!_OS, but as always, it's a good idea to have a backup of your important data before making system changes. If you run into any issues or need further modifications, please let me know!
````

Both scripts ultimately didn't work, though I didn't give them clean environments to run in.

However, the process of creating them was a good exercise in understanding how to use Generative AI to research and implement a solution to a problem. 