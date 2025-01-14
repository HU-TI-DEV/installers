# program           : InstallSoftware.py
# purpose           : Install student development environment for OOPC, V2CPSE1, V2CPSE2 and V2THDE on Windows
# author            : Nico Verduin 2020-2021
# date              : 17-5-2021
# author            : Hagen Patzke 2022
# date              : 01-11-2022
# change            : Refactor code-example directory CMake List generation.
# author            : Hagen Patzke 2025
# date              : 12-01-2025
# latest change     : Replace find_executable with non-deprecated shutil/which for Python 3.12 and later,
#                     update file paths for GCC-WIN (SSL cert error) and GCC-ARM (file not found).
#
# GitLab LINK       : https://github.com/HU-TI-DEV/installers/blob/master/InstallSoftware.py
# DOCUMENTATIE      : https://github.com/HU-TI-DEV/installers/blob/master/doc/Installeren-Windows.pdf
#
import sys  # System functions

if sys.version_info.major != 3:
    raise Exception("Sorry, this Python script only supports Python 3. Installation aborted.")
#
# Now we can continue
import os.path  # Pathnames in Windows
import subprocess  # Call sub processes
import pathlib  # Path functions
import logging  # log
import struct  # Structs for system info
import shutil  # Shell utilities
import urllib.request  # Download file
import tarfile  # Unpack TAR (Tape ARchive) file

# Package distutils.spawn was removed in Python 3.12
# see https://github.com/aws/sagemaker-python-sdk/issues/3028
if sys.version_info.minor < 12:
    # 3.11 and earlier
    from distutils.spawn import find_executable as findExecutable
else:
    # 3.12 and later
    from shutil import which as findExecutable

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

Compilers = {
    "GCC-ARM":
        "https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-win32.zip",
    #   "https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2019q4/gcc-arm-none-eabi-9-2019-q4-major-win32.zip",
    "GCC-WIN":
        "https://www.nic.funet.fi/pub/mirrors/download.qt-project.org/development_releases/prebuilt/mingw_32/i686-7.3.0-release-posix-dwarf-rt_v5-rev0.7z",
    #   "http://ftp.vim.org/languages/qt/development_releases/prebuilt/mingw_32/i686-7.3.0-release-posix-dwarf-rt_v5-rev0.7z",
    "GCC-AVR":
        "https://github.com/CrustyAuklet/avr-libstdcxx/releases/download/v9.2.0/avr-gcc-9.2.0-P0829-x86_64-w64-mingw32.tar.gz",
    "SFML":
        "https://www.sfml-dev.org/files/SFML-2.5.1-windows-gcc-7.3.0-mingw-32-bit.zip"
}
CompilerPaths = {}


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def safepath(string):
    """
    :param string: Pathname, potentially containing spaces
    :return: string in quotes if it contained spaces and did not start with a quote.
    """
    string = string.strip()
    # This type of quoting causes a problem with subprocess.run.
    # Batch file PATH does not mind spaces, so for now we disable it:
    if 0:
        quote = '"'
        if (' ' in string) and (string[0] != quote):
            string = quote + string + quote
    return string


# determine environment
print((str(struct.calcsize("P") * 8) + " bit machine"))

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
CWD = str(pathlib.Path().absolute().resolve()) + "\\"

logger.info("Start installation")

# Prerequisites
logger.info("Verifying Python, 7zip, git are installed (PATH and elsewhere)")

# Make sure we have Python in the path
PythonInPath = False
PythonProgram = ""
executablePath = findExecutable("python.exe")
if executablePath is not None:
    PythonProgram = safepath(executablePath)
    PythonInPath = True

# Find 7z.exe (32 bit or 64 bit version)
ZipInPath = False
ZipProgram = ""
executablePath = findExecutable("7z.exe")
if executablePath is not None:
    ZipProgram = safepath(executablePath)
    ZipInPath = True
if not ZipInPath:
    for file in zipLocations:
        if os.path.exists(file):
            ZipProgram = file
            break

# Find git.exe
GitInPath = False
GitProgram = ""
executablePath = findExecutable("git.exe")
if executablePath is not None:
    GitProgram = safepath(executablePath)
    GitInPath = True
if GitProgram == "":
    for file in gitLocations:
        if os.path.exists(file):
            GitProgram = safepath(file)
            break

if PythonProgram == "":
    logger.info("Cannot find Python in the PATH. Cancelling installation")
else:
    logger.info("found  Python.exe : " + PythonProgram)

# Python MUST be in the PATH, but for 7z annd git we accept additional locations.

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

if "" in [PythonProgram, ZipProgram, GitProgram]:
    # We cannot continue
    logger.info("Required program not found. Installation aborted.")
    exit(1)

# Download and install our GIT repositories
logger.info("Downloading GIT repositories")
for repo in GitRepositories:
    repoName = repo[repo.rfind("/") + 1:repo.rfind(".")]
    if os.path.exists(repoName):
        logger.info("Skipping git clone. Repository " + repoName + " exists and is not empty.")
    else:
        logger.info("Start cloning repository " + repoName)
        process = subprocess.run([GitProgram, "clone", repo, repoName],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = str(process.stdout)
        logger.info(data[2:-3])
        # switch to different version for Catch2
        if repoName == "Catch2":
            logger.info("adjusting Catch2 - checkout v2.x")
            os.chdir(repoName)
            process = subprocess.run([GitProgram, "checkout", "v2.x"],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            os.chdir("..")

logger.info("Downloading and unpacking Compilers")
for compiler in Compilers:
    compilerURL = Compilers[compiler]
    # get our local file name
    compilerFile = compilerURL[compilerURL.rfind("/") + 1:]
    # add entry in CompilerPaths with our BIN path name for the custom make later on
    CompilerPaths[compiler] = compilerFile[:compilerFile.rfind(".")]
    # check if the zip file is already there
    if os.path.exists(compilerFile):
        logger.info("skipping download : " + compilerFile + " as it already exists")
        decompressable = True
    else:
        # not here yet, so download it
        logger.info("Downloading from : " + compilerURL + " into " + compilerFile)
        # get the filesize to be downloaded
        req = urllib.request.Request(compilerURL, method='HEAD')
        f = urllib.request.urlopen(req)
        fileSize = int(f.headers['Content-Length'])
        # start download
        urllib.request.urlretrieve(compilerURL, compilerFile)
        # check if filesizes are equal
        localsize = os.stat(compilerFile).st_size
        if localsize == fileSize:
            logger.info("Download " + compilerFile + " was successful")
            decompressable = True
        else:
            logger.info("Download " + compilerFile + " failed. Downloaded " + localsize + ", should be " + fileSize)
            decompressable = False
            # TODO: retry the download a number of times (?) if it fails
    # let's decompress the file if we can
    if decompressable:
        # extract in root of compilername
        foldername = compilerFile[0:compilerFile.rfind(".")]
        logger.info("Decompressing " + compilerFile + "...")
        # TODO: see if finding install directory is better choice
        # Special handling for SFML
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
                logger.info('  ' + line)
            # rename the folder to SFML-2.5.1-32
            logger.info("Rename SFML-2.5.1 to SFML-2.5.1-32")
            try:
                os.rename("SFML-2.5.1", "SFML-2.5.1-32")
            except:
                logger.error("FAIL Rename SFML-2.5.1 to SFML-2.5.1-32, trying copy-and-delete")
                # Observation on HU employee laptop:
                # The rename is giving problems concerning rights (WinError 5).
                # For now, let's copy the folder and delete the original.
                copytree("sfml-2.5.1", "sfml-2.5.1-32")
                shutil.rmtree('SFML-2.5.1', ignore_errors=True)
        elif compilerFile.endswith('.tar.gz'):
            tar = tarfile.open(compilerFile)
            # get filestructure (we need the root)
            filelist = tar.getnames()
            # For TAR files (AVR Compiler) we use the pathname from the TAR file
            CompilerPaths[compiler] = filelist[0]
            # unpack everything
            tar.extractall()
            tar.close()
            logger.info(compiler + " installed")
        elif compilerFile.endswith('.7z') or compilerFile.endswith('.zip'):  # not SFML-2.5.1
            process = subprocess.run(
                [ZipProgram, "x", compilerFile, "-o" + foldername, "-y"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            data = str(process.stdout)[2:-3].replace('\\r', '').replace('\\n', '\n').splitlines()
            for line in data:
                logger.info('  ' + line)
logger.info("Downloaded and unpacked Compilers")

# Special operation for the windows GCC-WIN compiler
for compiler in Compilers:
    if compiler == "GCC-WIN":
        # we have to check if it is the 32 or 64 bit compiler
        if os.path.exists(CompilerPaths[compiler] + "\\mingw32"):
            CompilerPaths[compiler] = CompilerPaths[compiler] + "\\mingw32"
        else:
            CompilerPaths[compiler] = CompilerPaths[compiler] + "\\mingw64"
    logger.info("GCC-WIN variant: " + CompilerPaths[compiler])

# create Makefile.custom in bmptk
logger.info("Building bmptk\\Makefile.custom")

with open("bmptk\\Makefile.local") as makefile:
    makeLines = makefile.readlines()

windowsPart = False
with open("bmptk\\Makefile.custom", "wt") as custom:
    for line in makeLines:
        line = line.strip()
        # Flag the Windows part for processing
        if windowsPart:
            if "else" in line:
                windowsPart = False
        else:  # not in windowsPart
            if "ifeq ($(OS),Windows_NT" in line:
                windowsPart = True
        # Process the line as appropriate
        outputLine = line
        commentLine = (len(line) < 1) or (line.startswith("#"))
        if windowsPart and not commentLine:
            # if a line starts with a compiler definition, change it
            for compiler in Compilers:
                if line.startswith(compiler):
                    outputLine = "   " + compiler + "          ?= ..\\..\\" + CompilerPaths[compiler]
        custom.write(outputLine + "\n")

logger.info("Built Makefile.custom.")

logger.info("Creating set_env.bat file...")
with open('set_env.bat', 'wt') as batfile:
    pathSeparator = ';'
    batfile.write('@echo off\n')
    if not GitInPath:
        GitPath = os.path.dirname(GitProgram)
        batfile.write('SET PATH=%PATH%' + pathSeparator + safepath(GitPath) + '\n')
    if not ZipInPath:
        ZipPath = os.path.dirname(ZipProgram)
        batfile.write('SET PATH=%PATH%' + pathSeparator + safepath(ZipPath) + '\n')
    batfile.write('SET PATH=%PATH%' + pathSeparator + safepath(CWD + 'bmptk\\tools') + '\n')
    batfile.write('SET HCT=' + safepath(CWD + 'HCT') + '\n')
logger.info("Created set_env.bat file.")

logger.info("Prepare example folders for CodeLite and HCT...")
example_folders = ["v1oopc-examples", "v2cpse1-examples", "v2cpse2-examples", "v2thde-examples"]
# Add HCT CMake Lists to all example folders
with open("HCT/Voorbeeld_CMakeLists.txt", "rt") as ctfile:
    cmake_template = ctfile.read()
# Now use the CMake List template file to create a CMake List per project
for ex_folder in example_folders:
    logger.info("processing codelite update " + ex_folder)
    os.chdir(ex_folder)
    process = subprocess.run([PythonProgram, "../bmptk/tools/bmptk-mef.py", "-os", "windows"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = process.stdout.splitlines()
    for line in data:
        if isinstance(line, bytes):
            line = line.decode('latin-1')
        logger.info('  ' + line)
    with open('CMakeLists.txt', "wt") as cmlfile:
        cmlfile.write(cmake_template.replace("your-project-name", ex_folder))
    os.chdir("..")
logger.info("Prepared example folders for CodeLite and HCT.")

# done
logger.info("Execute set_env.bat to prepare your environment whenever opening a command shell.")
logger.info("Alternatively you can add the HCT environment variable, plus any the missing program"
            "directories to the PATH variable in your user environment.")
logger.info("Installation complete.\n")
