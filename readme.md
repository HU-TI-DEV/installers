To start with bmptk/hwib on Ubuntu under VMware:

- get WMware workstation player
- get the Ubuntu 18.04.2 LTS ISO from https://www.ubuntu.com/download/desktop
- create an image from the iso (remember the password!) - this will take some time...
- log in, open a terminal, click through the friendly welcome screens
- run these commands:
   - sudo apt -y install git
   - git clone https://www.github.com/wovo/installers
   - chmod 777 installers/ubuntu
   - sudo installers/ubuntu
   (this takes some time)
   
- to verify a native build run these commands:
   - cd ~/v1oopc-examples/00-00-hello
   - make run 
   (after building the executable should run and print "Hello world")
- to verify a build for the Arduino Due connect it and run these commands:
   (VMware must have the focus while you plug in the Arduino)
   - cd ~/v1oopc-examples/*-blink-hwlib
   - make run 
   (after building the executable should download to the Due and the LED should blink)
- to verify CodeLite
   - create
   - start codelite
   - run
   - first time only: select some toolchain (g++ is OK)
   

   
- due serial
- uno blink
- uno serial
- download v1oopc-examples   
- codelite & python

- for convenience: set the Firefox start pagina to the hwlib documentation
   - cd ~/hwlib
   - firefox index.html
   - settings->prefrences->home->homepage:custom urls->use current page
   