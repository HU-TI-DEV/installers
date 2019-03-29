To start with bmptk/hwib on Ubuntu under VMware:

- get WMware workstation player
- get the Ubuntu 18.04.2 LTS ISO from https://www.ubuntu.com/download/desktop
- create an image from the iso (remember the password!) - this will take some time...
- log in, open a terminal, click through the friendly welcome screens, run these commands:
   - sudo apt -y install git
   - git clone https://www.github.com/wovo/installers
   - sudo installers/ubuntu