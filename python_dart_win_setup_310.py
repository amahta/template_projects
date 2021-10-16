import os
import subprocess
import zipfile
import requests


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
../python
./Lib/site-packages
python310.zip
.

import site
'''

####################################################################################################
PYTHON_APP_CONTENTS = '''
import json
CMD_EXIT = 0
CMD_ADD = 1
CMD_MUL = 2
STREAM_START = "`S`T`R`E`A`M`43fd93e2-0932-4fe6-a0b6-a4320aca6aa0`S`T`A`R`T`"
STREAM_END = "`S`T`R`E`A`M`43fd93e2-0932-4fe6-a0b6-a4320aca6aa0`E`N`D`"
def add(a, b):
    return {"result": a + b}
def mul(a, b):
    return {"result": a * b}
def run(command):
    if command["cmd"] == CMD_EXIT:
        exit()
    elif command["cmd"] == CMD_ADD:
        return add(command["a"], command["b"])
    elif command["cmd"] == CMD_MUL:
        return mul(command["a"], command["b"])
    else:
        return {"error": "Unknown command."}
if __name__ == "__main__":
    while True:
        cmd = input()
        cmd = json.loads(cmd)
        try:
            result = run(cmd)
        except Exception as e:
            result = {"exception": e.__str__()}
        result = json.dumps(result)
        print(STREAM_START + result + STREAM_END)
'''

####################################################################################################
PYTHON_DART_CONTENTS = '''
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:mutex/mutex.dart';
class Python {
  static const _STDOUT_STREAM_START = "`S`T`R`E`A`M`43fd93e2-0932-4fe6-a0b6-a4320aca6aa0`S`T`A`R`T`";
  static const _STDOUT_STREAM_END = "`S`T`R`E`A`M`43fd93e2-0932-4fe6-a0b6-a4320aca6aa0`E`N`D`";
  static const _CMD_EXIT = 0;
  static const _CMD_ADD = 1;
  static const _CMD_MUL = 2;
  var _resultCompleter = Completer();
  var _result = "";
  late Process _process;
  final _runCmdMutex = Mutex();
  Future<bool> initialize() async {
    return await _runCmdMutex.protect<bool>(() async {
      return await _initializeUnprotected();
    });
  }
  Future<bool> _initializeUnprotected() async {
    _process =
        await Process.start("./python310x64/python.exe", ["./python/app.py"]);
    _process.stdout.transform(utf8.decoder).forEach((element) {
      //print(element);
      _result += element;
      if (_result.contains(_STDOUT_STREAM_END) &&
          !_resultCompleter.isCompleted) {
        _resultCompleter.complete(_result
            .split(_STDOUT_STREAM_START)[1]
            .replaceAll(_STDOUT_STREAM_END, "")
            .trim());
      }
    });
    _process.stderr.transform(utf8.decoder).forEach((element) {
      //print(element);
    });
    return true;
  }
  Future<dynamic> _runCommand(dynamic command) async {
    return await _runCmdMutex.protect<dynamic>(() async {
      return await _runCommandUnprotected(command);
    });
  }
  Future<dynamic> _runCommandUnprotected(dynamic command) async {
    final jsCommand = jsonEncode(command);
    _resultCompleter = Completer();
    _result = "";
    _process.stdin.writeln(jsCommand);
    final jsResult = await _resultCompleter.future;
    return jsonDecode(jsResult);
  }
  Future<int> add(int a, int b) async {
    var command = {"cmd": _CMD_ADD, "a": a, "b": b};
    final result = await _runCommand(command);
    return result["result"];
  }
  Future<int> mul(int a, int b) async {
    var command = {"cmd": _CMD_MUL, "a": a, "b": b};
    final result = await _runCommand(command);
    return result["result"];
  }
}
'''

####################################################################################################
PYTHON_TEST_CONTENTS = '''
import 'package:flutter_test/flutter_test.dart';
import 'package:YOUR_PROJECT_NAME/python.dart';
void main() {
  test("Test Add", () async {
    final python = Python();
    final initialized = await python.initialize();
    expect(initialized, true);
    final result = await python.add(10, 10);
    expect(result, 20);
  });
  test("Test Multiply", () async {
    final python = Python();
    final initialized = await python.initialize();
    expect(initialized, true);
    final result = await python.mul(10, 10);
    expect(result, 100);
  });
}
'''

####################################################################################################
if __name__ == "__main__":

    # parameters
    python_download_url = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip"
    python_download_path = "./python.zip"
    python_path = "./python310x64"
    python_pth_file = python_path + "/python310._pth"

    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = python_path + "/get-pip.py"

    python_scripts_path = "./python"
    python_app_path = python_scripts_path + "/app.py"

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
    os.mkdir(python_scripts_path)
    create_or_replace_txt_file(python_app_path, PYTHON_APP_CONTENTS)

    # Create Python class for Dart
    create_or_replace_txt_file(python_dart_path, PYTHON_DART_CONTENTS)

    # Create Python class tests
    create_or_replace_txt_file(python_test_dart_path, PYTHON_TEST_CONTENTS)

    print(
        '''
        
        Add the following dependencies to pubspec.yaml:
        mutex: ^3.0.0
        
        Add the following to main.cpp in windows folder:
        // https://stackoverflow.com/questions/67082272/dart-how-to-hide-cmd-when-using-process-run
        else {
            AllocConsole();
            ShowWindow(GetConsoleWindow(), SW_HIDE);
        }
        
        Add the following to .gitignore:
        /python310x64/
        
        Check out tests to see how things work:
        Replace your project name for the import line in tests.
        
        ''')
