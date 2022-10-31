# program           : InstallSoftware.py
# purpose           : Install student development environment for OOPC, V2CSPE1 and V2CSPE2 under Windows
# author            : Nico Verduin 2020-2021
# date              : 17-5-2021
# latest change     : Andere AVR compiler downloaden die STD ondersteunt
#
import winreg  # lezen van de windows registry
import os.path  # pad namen in Windows
import subprocess  # Aanroepen sub processem
import pathlib  # Path functies
import logging  # logger info
import sys  # Systeem functies
import struct  # structs voor systeem info
import shutil  # Shell utilities
import distutils.spawn  # Aanroepen sub processem
import urllib.request  # nodig om een file te downloaden
import tarfile  # nodig om een tar file uit te pakken


zipLocations = ["C:\\Program Files\\7-Zip\\7z.exe", "C:\\Program Files (x86)\\7-Zip\\7z.exe"]

gitLocations = ["C:\\Program Files\\Git\\cmd\\git.exe", "C:\\Program Files (x86)\\Git\\cmd\\git.exe"]

GitRepositories = ["https://github.com/HU-TI-DEV/bmptk.git",
                "https://github.com/HU-TI-DEV/hwlib.git",
                "https://github.com/HU-TI-DEV/rtos.git",
                "https://github.com/HU-TI-DEV/v1oopc-examples.git",
                "https://github.com/HU-TI-DEV/v2cpse1-examples.git",
                "https://github.com/HU-TI-DEV/v2cpse2-examples.git",
                "https://github.com/HU-TI-DEV/v2thde-examples.git",
                "https://github.com/catchorg/Catch2.git",
                "https://github.com/HU-TI-DEV/HCT.git"]

AVR_COMPILER = "https://github.com/CrustyAuklet/avr-libstdcxx/releases/download/v9.2.0/avr-gcc-9.2.0-P0829-x86_64-w64-mingw32.tar.gz"

Compilers = [["GCC-ARM",
              "https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-win32.zip"],
             ["GCC-WIN",
              "http://ftp.vim.org/languages/qt/development_releases/prebuilt/mingw_32/i686-7.3.0-release-posix-dwarf-rt_v5-rev0.7z"],
             ["GCC-AVR", ""],
             ["SFML", "https://www.sfml-dev.org/files/SFML-2.5.1-windows-gcc-7.3.0-mingw-32-bit.zip"]]




def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


# determine environment
print((str(struct.calcsize("P") * 8) + " Bits machine"))

# Create our logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='Install.log',
                    filemode='w')
logger = logging.getLogger()
# copy logging output to stdout
logger.addHandler(logging.StreamHandler(sys.stdout))

# get current working folder
CWD = pathlib.Path().absolute().__str__() + "\\"

logger.info("Start installation")

# Prerequisites
logger.info(("Verifying 7zip and git are installed"))

# Make sure we have Python in the path
PythonProgram = ""
executablePath = distutils.spawn.find_executable("python.exe")
if executablePath is not None:
    PythonProgram = executablePath


# find 7z.exe (32 bit or 64 bit version)
ZipProgram = ""
for file in zipLocations:
    if os.path.exists(file):
        ZipProgram = file

if ZipProgram == "":
    executablePath = distutils.spawn.find_executable("7z.exe")
    if executablePath is not None:
        ZipProgram = executablePath


# find git.exe
GitProgram = ""
for file in gitLocations:
    if os.path.exists(file):
        GitProgram = file

if GitProgram == "":
    executablePath = distutils.spawn.find_executable("git.exe")
    if executablePath is not None:
        GitProgram = executablePath


if PythonProgram == "":
    logger.info("Cannot find Python in the PATH. Cancelling installation")
else:
    logger.info("found  Python.exe : " + PythonProgram)

if ZipProgram == "":
    logger.info("Cannot find installation of 7z. Cancelling installation")
    logger.info("Please install 7z from https://www.7-zip.org/download.html")
else:
    logger.info("found  7z program : " + ZipProgram)

if GitProgram == "":
    logger.info("Cannot find installation of GIT. Cancelling installation")
    logger.info("Please install Git from https:/desktop.github.com/")
else:
    logger.info("found GIT program : " + GitProgram)

if "" in [ PythonProgram, ZipProgram, GitProgram ]:
    # We cannot continue
    logger.info("Required program not found. Installation aborted.")
    exit(1)



# Download and install our GIT repositories
logger.info("Downloading GIT repositories")
for repo in GitRepositories:
    repoName = repo[repo.rfind("/") + 1:repo.rfind(".")]
    if os.path.exists(repoName):
        logger.info("Skipping git clone. Repository " + repoName + " exists and/or is not empty.")
    else:
        process = subprocess.run([GitProgram, "clone", repo, repoName], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = str(process.stdout)
        logger.info(data[2:-3])
        # switch to different version for Catch2
        if repoName == "Catch2":
            logger.info("adjusting Catch2 - checkout v2.x")
            os.chdir(repoName)
            os.system(GitProgram + ' checkout v2.x')
            os.chdir("..")

# Download AVR Compiler and unpack
logger.info("Download AVR Compiler")
localAVRCompilerName = "AVR-Compiler.tar.gz"
urllib.request.urlretrieve(AVR_COMPILER, localAVRCompilerName)
logger.info("Downloaded. Installing...")
tar = tarfile.open(localAVRCompilerName)
# get filestructure (we need the root)
filelist = tar.getnames()
AVR_Folder = filelist[0]
# unpack everything
tar.extractall()
tar.close()
logger.info("AVR Compiler installed")

logger.info("Downloading other Compilers")
for compiler in Compilers:
    # ignore the GCC-AVR compiler
    if (compiler[0] != "GCC-AVR"):
        # get our local file name
        compilerFile = compiler[1][compiler[1].rfind("/") + 1:]
        # add column in compiler with our BIN path name for the custom make later on
        makefileName = compilerFile[:compilerFile.rfind(".")]
        compiler.append(makefileName)
        # check if the zip file is already there
        if os.path.exists(compilerFile):
            logger.info("skipping download : " + compilerFile + " as it already exists")
            decompressable = True
        else:
            # not here yet, so download it
            logger.info("Downloading from : " + compiler[1] + " into " + compilerFile)
            # get the filesize to be downloaded
            req = urllib.request.Request(compiler[1], method='HEAD')
            f = urllib.request.urlopen(req)
            fileSize = int(f.headers['Content-Length'])
            # start download
            urllib.request.urlretrieve(compiler[1], compilerFile)
            # check if filesizes are equal
            if os.stat(compilerFile).st_size == fileSize:
                logger.info("Download " + compilerFile + " was successful")
                decompressable = True
            else:
                logger.info("Download " + compilerFile + " failed. Downloaded " + os.stat(
                    compilerFile).st_size + " should be : " + fileSize)
                decompressable = False

        # if it seems decompressable, may as well do it
        if decompressable:
            # extract in root of compilername
            foldername = compilerFile[0:compilerFile.rfind(".")]
            logger.info("Decompressing " + compilerFile + "...")
            #
            # TODO: see if finding install directory is better choice
            #
            if foldername.find("SFML-2.5.1") >= 0:
                # delete any old SFML-2.5.1-32 folder
                logger.info("Delete any existing SFML-2.5.1-32 folder")
                shutil.rmtree('SFML-2.5.1', ignore_errors=True)
                process = subprocess.run(
                    [ZipProgram, "x", compilerFile, "SFML-2.5.1", "-o.", "-y"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                # we get more output lines but need some cleaning
                data = str(process.stdout)[2:-3].replace('\\r', '').replace('\\n', '\n').splitlines()
                for line in data:
                    logger.info(line)

                # rename the folder to SFML-2.5.1-32
                logger.info("Rename SFML-2.5.1 to SFML-2.5.1-32")

                #
                # The rename is giving problems concerning rights. Just copy the folder and delete the original
                copytree("sfml-2.5.1", "sfml-2.5.1-32")
                # os.rename("SFML-2.5.1", "SFML-2.5.1-32")

            else:
                process = subprocess.run(
                    [ZipProgram, "x", compilerFile, "-o" + foldername, "-y"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                data = str(process.stdout)[2:-3].replace('\\r', '').replace('\\n', '\n').splitlines()
                for line in data:
                    logger.info(line)

# Special operation for the windows GCC-WIN compiler
for compiler in Compilers:
    if compiler[0] == "GCC-WIN":
        # we have to check if it is the 32 or 64 bit compiler
        if os.path.exists(compiler[2] + "\\mingw32"):
            compiler[2] = compiler[2] + "\\mingw32"
        else:
            compiler[2] = compiler[2] + "\\mingw64"
    if compiler[0] == "GCC-AVR":
        compiler.append(AVR_Folder)

    print(compiler[2])

    # special fix for AVR compilers
    # if compiler[0] == "GCC-AVR":
    #     if (os.path.exists(compiler[2] + "\\" + compiler[2])):
    #         logger.info("AVR Compiler unzipped one level too deep")
    #         # move the compiler one level upwards
    #         source_dir = compiler[2] + "\\" + compiler[2]
    #         target_dir = compiler[2]
    #         file_names = os.listdir(source_dir)
    #
    #         for file_name in file_names:
    #             shutil.move(os.path.join(source_dir, file_name), target_dir)
    #         logger.info("AVR Compiler moved one level upwards")
    #
    #         # delete too deep compiler folder
    #         shutil.rmtree(source_dir)
    #         logger.info("Old AVR-GCC compiler folder deleted")
    #

# create Makefile.custom in bmptk
makefile = open("bmptk\\Makefile.local", "r")
custom = open("bmptk\\Makefile.custom", "w")

logger.info("Building Makefile.custom")
windowsPart = False

makeLines = makefile.read().splitlines()
for line in makeLines:
    outputLine = line
    line = line.strip()
    # check if this is the Windows part
    if line.find("ifeq ($(OS),Windows_NT") >= 0:
        windowsPart = True
    # only process the Windows part
    if windowsPart:
        if line.find("else") >= 0:
            windowsPart = False
        else:
            # do nothing with comment lines
            if len(line) != 0:
                if line[0] != "#":
                    # scan if it is a compiler definition
                    for compiler in Compilers:
                        searchArgument = compiler[0]
                        if (len(line) >= len(searchArgument)):
                            if line[0:len(searchArgument)] == compiler[0]:
                                outputLine = "   " + compiler[0] + "          ?= ..\\..\\" + compiler[2]

    custom.write(outputLine + "\n")

makefile.close()
custom.close()
logger.info("Building Makefile.custom completed")

if 0:
    # *** Adjusting the PATH ***
    logger.info("Update PATH in Windows Registry")
    pathSeparator = ";"
    regEditFile = "PathUpdate.reg"
    logger.info(regEditFile + " Created");
    pathNeedsUpdate = False

    logger.info("Read current PATH in Windows Registry")
    # Read the registry for our system path variable
    root_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
    [Pathname, regtype] = (winreg.QueryValueEx(root_key, "Path"))
    winreg.CloseKey(root_key)

    logger.info("Update PATH in Environment")
    pathSeparator = ";"
    regEditFile = "PathUpdate.reg"
    logger.info(regEditFile + " Created");
    pathNeedsUpdate = False

    # change it into a list
    Paths = Pathname.split(pathSeparator)

    logger.info("Remove any references to BMPTK")
    # remove any path that refers to \BMPTK\
    for str in Paths:
        y = str.upper()
        if y.find("\\BMPTK\\") >= 0:
            pathNeedsUpdate = True
            logger.info("Deleted " + str)
            Paths.remove(str)
            logger.info("Path will be updated")

    logger.info("Add new BMPTK path : " + CWD + "bmptk\\tools")
    # rebuild our path string
    Pathname = CWD + 'bmptk\\tools' + pathSeparator
    for str in Paths:
        Pathname += str + pathSeparator

    # Change a single backslash to double (special character)
    convertedPathname = Pathname.replace('\\', '\\\\')

    logger.info(convertedPathname)

    logger.info("Create .REG file")
    # build a new registration file
    outputFile = open(regEditFile, "w")
    outputFile.write("Windows Registry Editor Version 5.00\n\n")
    outputFile.write("[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment]\n")

    # delete old Path value
    outputFile.write('\"Path\"=-\n')

    # add our new Path parameter
    outputFile.write('\"Path\"=\"' + convertedPathname + '\"\n')

    # Add an environment variable for HCT
    convertedWorkDir = CWD.replace("\\", "\\\\")
    HCT_PATH = convertedWorkDir + 'HCT'
    outputFile.write('\"HCT\"=\"' + HCT_PATH + '\"\n\n')

    outputFile.close()

    logger.info("Reg file is : " + regEditFile)

    # creat an update batch file. Must be in a CMD box with admin rights
    logger.info("Execute pathupdate.bat when this program is finished")

    # create our bat file
    batfile = open("pathupdate.bat", "w")
    batfile.write("@echo off\n")
    batfile.write("echo Please enter OK, Ja, Yes or something like this when requested.\n")
    batfile.write("pause\n")
    batfile.write("%windir%\\regedit.exe pathupdate.reg \n")
    batfile.write("echo Please reboot the computer\n")
    batfile.write("pause\n")
    # batfile.write("del PathUpdate.reg\n")
    # batfile.write("del PathUpdate.bat\n")
    batfile.close();
else:
    logger.info("Creating set_env.bat file...")
    pathSeparator = ";"
    # Check if we need to quote the pathname of the directory
    if CWD[0] != '"' and ' ' in CWD:
        quote = '"'
    else:
        quote = ''
    batfile = open('set_env.bat', 'w')
    batfile.write('@echo off\n')
    batfile.write('SET PATH=%PATH%'+ pathSeparator + quote + CWD + 'bmptk\\tools' + quote +'\n')
    GitPath = os.path.dirname(GitProgram)
    batfile.write('SET PATH=%PATH%'+ pathSeparator + GitPath +'\n')
    batfile.write('SET HCT='+ CWD + 'HCT\n')
    batfile.close()
    logger.info("Execute set_env.bat to prepare your environment whenever opening a command shell.")

# prepare example folders for codelite

logger.info("processing codelite update v1oopc-examples")
os.chdir("v1oopc-examples")
process = subprocess.run([PythonProgram, "./../bmptk/tools/bmptk-mef.py", "-os", "windows"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

data = process.stdout.splitlines()
for line in data:
    logger.info(line)

logger.info("processing codelite update v2cpse1-examples")
os.chdir("../v2cpse1-examples")
process = subprocess.run([PythonProgram, "./../bmptk/tools/bmptk-mef.py", "-os", "windows"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

data = process.stdout.splitlines()
for line in data:
    logger.info(line)

logger.info("processing codelite update v2cpse2-examples")
os.chdir("../v2cpse2-examples")
process = subprocess.run([PythonProgram, "./../bmptk/tools/bmptk-mef.py", "-os", "windows"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

data = process.stdout.splitlines()
for line in data:
    logger.info(line)

logger.info("processing codelite update v2thde-examples")
os.chdir("../v2thde-examples")
process = subprocess.run([PythonProgram, "./../bmptk/tools/bmptk-mef.py", "-os", "windows"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

data = process.stdout.splitlines()
for line in data:
    logger.info(line)

# Add HCT cmakelists to all example folders
logger.info("Adding HCT to example folders")

os.chdir("../")

voorbeeld_cmake_contents = open("./HCT/Voorbeeld_CMakeLists.txt", "r").read()

example_folders = [
    "v1oopc-examples",
    "v2cpse1-examples",
    "v2cpse2-examples",
    "v2thde-examples"
]

for ex_folder in example_folders:
    open(('./%s/CMakeLists.txt' % ex_folder), 'w').write(
        voorbeeld_cmake_contents.replace("your-project-name", ex_folder))

# done


logger.info("Installation complete.\n")
