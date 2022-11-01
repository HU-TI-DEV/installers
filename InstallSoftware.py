# program           : InstallSoftware.py
# purpose           : Install student development environment for OOPC, V2CPSE1, V2CPSE2 and V2THDE on Windows
# author            : Nico Verduin 2020-2021
# date              : 17-5-2021
# author            : Hagen Patzke 2022
# date              : 01-11-2022
# latest change     : Refactor code-example directory CMake List generation.
#
import os.path  # Pathnames in Windows
import subprocess  # Call sub processes
import pathlib  # Path functions
import logging  # log
import sys  # System functions
import struct  # Structs for system info
import shutil  # Shell utilities
import distutils.spawn  # Invoke sub processes
import urllib.request  # Download file
import tarfile  # Unpack TAR (Tape ARchive) file


zipLocations = ["C:\\Program Files\\7-Zip\\7z.exe",
                "C:\\Program Files (x86)\\7-Zip\\7z.exe"]

gitLocations = ["C:\\Program Files\\Git\\cmd\\git.exe",
                "C:\\Program Files (x86)\\Git\\cmd\\git.exe"]

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
             ["GCC-AVR",
              ""],
             ["SFML",
              "https://www.sfml-dev.org/files/SFML-2.5.1-windows-gcc-7.3.0-mingw-32-bit.zip"]]




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
        process = subprocess.run([GitProgram, "clone", repo, repoName],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = str(process.stdout)
        logger.info(data[2:-3])
        # switch to different version for Catch2
        if repoName == "Catch2":
            logger.info("adjusting Catch2 - checkout v2.x")
            os.chdir(repoName)
            os.system(GitProgram + ' checkout v2.x')
            os.chdir("..")

logger.info("Downloading Compilers")
for compiler in Compilers:
    if compiler[0] == "GCC-AVR":
        logger.info("Download AVR Compiler")
        compilerFile = "AVR-Compiler.tar.gz"
        if os.path.exists(compilerFile):
            logger.info("skipping download : " + compilerFile + " as it already exists")
        else:
            urllib.request.urlretrieve(AVR_COMPILER, compilerFile)
            logger.info("Downloaded. Installing...")
        tar = tarfile.open(compilerFile)
        # get filestructure (we need the root)
        filelist = tar.getnames()
        AVR_Folder = filelist[0]
        # unpack everything
        tar.extractall()
        tar.close()
        compiler.append(AVR_Folder)
        logger.info("AVR Compiler installed")
    else:
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
            # TODO: see if finding install directory is better choice
            if foldername.find("SFML-2.5.1") >= 0:
                # delete any old SFML-2.5.1-32 folder
                logger.info("Delete any existing SFML-2.5.1-32 folder")
                shutil.rmtree('SFML-2.5.1-32', ignore_errors=True)
                logger.info("Delete any existing SFML-2.5.1 folder")
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
                os.rename("SFML-2.5.1", "SFML-2.5.1-32")
                # HP comment: if we did not remove the old SFML-2.5.1-32 folder, there is a name clash!
                # The rename is giving problems concerning rights. Just copy the folder and delete the original
                # copytree("sfml-2.5.1", "sfml-2.5.1-32")
                # shutil.rmtree('SFML-2.5.1', ignore_errors=True)
            else:  # not SFML-2.5.1
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
    logger.info("GCC-WIN variant: " + compiler[2])

# create Makefile.custom in bmptk
logger.info("Building bmptk\\Makefile.custom")

with open("bmptk\\Makefile.local") as makefile:
    makeLines = makefile.readlines()

windowsPart = False
custom = open("bmptk\\Makefile.custom", "wt")

for line in makeLines:
    line = line.strip()
    # skip empty lines and comment lines
    if (len(line) < 1) or (line[0] == "#"):
        continue
    # check if this is the Windows part
    if line.find("ifeq ($(OS),Windows_NT") >= 0:
        windowsPart = True
    # only process the Windows part
    if not windowsPart:
        continue
    if line.find("else") >= 0:
        windowsPart = False
        continue
    # scan if it is a compiler definition
    outputLine = line
    for compiler in Compilers:
        searchArgument = compiler[0]
        if len(line) >= len(searchArgument):
            if line[0:len(searchArgument)] == searchArgument:
                outputLine = "   " + compiler[0] + "          ?= ..\\..\\" + compiler[2]
    custom.write(outputLine + "\n")

custom.close()
logger.info("Built Makefile.custom.")

logger.info("Creating set_env.bat file...")
pathSeparator = ";"
# Check if we need to quote the pathname of the directory
quote = '"' if CWD[0] != '"' and ' ' in CWD else ''
with open('set_env.bat', 'wt') as batfile:
    batfile.write('@echo off\n')
    batfile.write('SET PATH=%PATH%' + pathSeparator + quote + CWD + 'bmptk\\tools' + quote + '\n')
    GitPath = os.path.dirname(GitProgram)
    batfile.write('SET PATH=%PATH%' + pathSeparator + GitPath + '\n')
    batfile.write('SET HCT=' + CWD + 'HCT\n')
logger.info("Created set_env.bat file.")

logger.info("Prepare example folders for CodeLite and HCT...")
example_folders = ["v1oopc-examples", "v2cpse1-examples", "v2cpse2-examples", "v2thde-examples"]
# Add HCT CMake Lists to all example folders
with open("../HCT/Voorbeeld_CMakeLists.txt", "rt") as ctfile:
    cmake_template = ctfile.read()
# Now use the CMake List template file to create a CMake List per project
for ex_folder in example_folders:
    logger.info("processing codelite update " + ex_folder)
    os.chdir(ex_folder)
    process = subprocess.run([PythonProgram, "../bmptk/tools/bmptk-mef.py", "-os", "windows"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = process.stdout.splitlines()
    for line in data:
        if type(line) == "<class 'bytes'>":
            line.decode('latin-1')
        logger.info(line)
    with open('CMakeLists.txt', "wt") as cmlfile:
        cmlfile.write(cmake_template.replace("your-project-name", ex_folder))
    os.chdir("..")
logger.info("Prepared example folders for CodeLite and HCT.")

# done
logger.info("Execute set_env.bat to prepare your environment whenever opening a command shell.")
logger.info("Installation complete.\n")
