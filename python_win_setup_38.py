import zipfile, requests, os, subprocess


####################################################################################################
def create_or_replace_txt_file(path: str, contents: str):
    with open(path, "wt") as f:
        f.write(contents)


####################################################################################################
def download_url(url: str, path: str):
    the_file = requests.get(url)
    with open(path, 'wb') as f:
        f.write(the_file.content)


####################################################################################################
def unzip_file(zip_path: str, dest_path: str):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest_path)


####################################################################################################
def run_process(working_dir: str, args: list):
    original_cwd = os.getcwd()
    os.chdir(working_dir)
    subprocess.call(args)
    os.chdir(original_cwd)


####################################################################################################
PYTHON_PTH_CONTENTS = '''..
./Lib/site-packages
python38.zip
.

import site

'''

####################################################################################################
PYTHON_APP_CONTENTS = '''
if __name__ == "__main__":
    print("Hello World")

'''

####################################################################################################
if __name__ == "__main__":

    # parameters
    python_download_url = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip"
    python_download_path = "./python.zip"
    python_path = "./python38x64"
    python_pth_file = python_path + "/python38._pth"

    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = python_path + "/get-pip.py"

    python_app_path = "./app.py"

    python_dart_path = "./lib/python.dart"
    python_test_dart_path = "./test/python_test.dart"

    # Run some checks first
    if os.path.isdir(python_path):
        print(python_path + " already exists. You've ran this script before.")
        exit(-1)

    # Get Python
    download_url(python_download_url, python_download_path)
    unzip_file(python_download_path, python_path)
    os.remove(python_download_path)

    # Setup ._pth file
    create_or_replace_txt_file(python_pth_file, PYTHON_PTH_CONTENTS)

    # Download and run get-pip.py
    download_url(get_pip_url, get_pip_path)
    run_process(python_path, ["./python.exe", "./get-pip.py"])

    # Create Python code template
    create_or_replace_txt_file(python_app_path, PYTHON_APP_CONTENTS)

    print(
        '''        
        Add the following to .gitignore:
        ./python38x64      
        ''')
