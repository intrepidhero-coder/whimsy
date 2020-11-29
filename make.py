import datetime
import os
import shutil as sh
import subprocess as sub
import tempfile
import time
import zipfile

NAME = "whimsy"
SEED = "12345"
MAIN = "gui"


def makeExe():
    """ This process makes the generated EXE file and zipfile distribution reproducible """
    repo = os.getcwd()
    tag = "1.0"

    # make a temporary directory for the build
    tempdir = tempfile.TemporaryDirectory()
    cwd = tempdir.name
    print("Make temp directory: ", cwd)

    # create virtual environment
    print("Creating venv")
    pythonbin = (os.name == "posix") and "python3" or "python"
    # TODO: Should specify version number
    sub.run([pythonbin, "-m", "venv", cwd])
    os.environ["VIRTUAL_ENV"] = cwd
    os.environ["PATH"] = os.path.join(cwd, "bin") + os.pathsep + os.environ["PATH"]
    # unset PYTHONHOME
    # are PYTHONLIBS, PYTHONPATH set?
    # not set on my systems (Debian 10, Win 10)
    sub.run(["pip", "install", "-r", "requirements.txt"])

    # get the name of the current checkout
    """
    checkout = sub.run(["git", "branch", "--list"], capture_output=True).stdout.decode("latin-1")
    tag = [field.split()[1] for field in checkout if field.startswith("*")][0]
    yesno = input("Is ({}) the correct tag? (y/n)".format(tag)).lower().strip()
    if yesno != "y":
        print("Abort")
        return

    # clone
    """
    cwd = os.path.join(cwd, "source")
    os.mkdir(cwd)
    result = sub.run(
        ["git", "clone", repo, cwd], capture_output=True
    )
    if not b"done." in result.stderr:
        print("Failed to clone {}".format(repo))
        print(result.stderr)
        return
    os.chdir(cwd)
    print("Cloned ", repo)

    """
    # get the date of the current checkout
    result = sub.run(["hg", "log", "-r", tag], capture_output=True)
    str_date = result.stdout.decode("latin-1").splitlines()[3][5:].strip()
    co_date = time.mktime(datetime.datetime.strptime(str_date, "%c %z").timetuple())
    """
    # run pyinstaller
    print("Running PyInstaller")
    os.environ["PYTHONHASHSEED"] = SEED
    # TODO: add excludes
    result = sub.run(
        ["pyinstaller", "--onefile", "--windowed", "--noconfirm", "--icon", "lighthouse.ico", "--name", NAME, MAIN + ".py",]
    )

    # build.txt to dist
    """
    open(os.path.join("dist", "build.txt"), "w").write(
        "Build: {} {}".format(checkout, str_date)
    )
    """

    # copy data files
    print("Copy files in data")
    #sh.copytree("data", os.path.join("dist", "data"))
    sh.copy("world.json", "dist") 
    sh.copy("noun_Lighthouse_1548448.png", "dist") 

    # write the changelog
    """
    print("Writing changelog.txt")
    result = sub.run(["hg", "log"], capture_output=True)
    open(os.path.join("dist", "changelog.txt"), "w").write(
        result.stdout.decode("latin-1")
    )
    """

    # zip up the dist folder
    print("Create .zip file")
    sh.move("dist", NAME)
    zip_filename = NAME + "_v" + tag + "_" + os.name + ".zip"
    zip_archive = zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
    filenames = []
    for root, dirs, files in os.walk(NAME):
        for f in files:
            filenames.append(os.path.join(root, f))
    # filenames are sorted so that the zipfile has consistent order
    filenames = sorted(filenames)
    for fullname in filenames:
        print("Adding: ", fullname)
        # file modified times are set to the date of the selected checkout
        #os.utime(fullname, times=(co_date, co_date))
        zip_archive.write(fullname)
    zip_archive.close()
    sh.copy(zip_filename, repo)

    # TODO: install script

    # update repo back to tip
    os.chdir(repo)
    print("Restore {} to tip".format(repo))
    #sub.run(["hg", "update"])

    print("****COMPLETE****")


if __name__ == "__main__":
    makeExe()
    # TODO: test target
    # TODO: debug target
    # TODO: linux target
    # TODO: support running windows build in wine
