import zipfile, requests, os, shutil, subprocess

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
python39.zip
.

import site

'''

####################################################################################################
PYTHON_APP_CONTENTS = '''
import json

CMD_EXIT = 0
CMD_ADD = 1
CMD_MUL = 2

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
        print(result + "`S`T`R`E`A`M` `E`N`D`")

'''

####################################################################################################
PYTHON_DART_CONTENTS = '''
import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:mutex/mutex.dart';

class Python {
  static const _STDOUT_STREAM_END = "`S`T`R`E`A`M` `E`N`D`";

  static const _CMD_EXIT = 0;
  static const _CMD_ADD = 1;
  static const _CMD_MUL = 2;

  var _resultCompleter = Completer();
  var _result = "";
  late Process _process;
  final _runCmdMutex = Mutex();

  Future<bool> initialize() async {
    _process = await Process.start("./python39x64/python.exe", ["./python/app.py"]);
    _process.stdout.transform(utf8.decoder).forEach((element) {
      _result += element;
      if (_result.contains(_STDOUT_STREAM_END) &&
          !_resultCompleter.isCompleted) {
        _resultCompleter
            .complete(_result.replaceAll(_STDOUT_STREAM_END, "").trim());
      }
    });
    return true;
  }

  Future<dynamic> _runCommand(dynamic command) async {
    return await _runCmdMutex.protect<dynamic>(() async {
      final jsCommand = jsonEncode(command);
      _resultCompleter = Completer();
      _result = "";
      _process.stdin.writeln(jsCommand);
      final jsResult = await _resultCompleter.future;
      return jsonDecode(jsResult);
    });
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

    # Get Python
    python_download_path = "./python.zip"
    download_url("https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-amd64.zip",
                 python_download_path)
    unzip_file(python_download_path, "./python39x64")

    # Setup ._pth file
    create_or_replace_txt_file("./python39x64/python39._pth", PYTHON_PTH_CONTENTS)

    # Download and run get-pip.py
    download_url("https://bootstrap.pypa.io/get-pip.py", "./python39x64/get-pip.py")
    run_process("./python39x64", ["./python.exe", "./get-pip.py"])

    # Create Python code template
    os.mkdir("./python")
    create_or_replace_txt_file("./python/app.py", PYTHON_APP_CONTENTS)

    # Create Python class for Dart
    create_or_replace_txt_file("./lib/python.dart", PYTHON_DART_CONTENTS)

    # Create Python class tests
    create_or_replace_txt_file("./test/python_test.dart", PYTHON_TEST_CONTENTS)

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
./python.zip
./python39x64

Check out tests to see how things work:
Replace your project name for the import line in tests.

''')