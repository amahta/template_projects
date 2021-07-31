import os
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
FLASK_APP_PY_CONTENTS = '''from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home_route():
    return "Hello World!", 200


if __name__ == "__main__":
    app.run()

'''

####################################################################################################
LIB_HOME_PAGE_CONTENTS = '''import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class HomePage extends StatefulWidget {
  HomePage({Key? key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  var text = "...";

  @override
  void initState() {
    super.initState();

    http.get(Uri.parse("http://localhost:5000")).then((response) {
      setState(() {
        text = response.body;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(text),
          ],
        ),
      ),
    );
  }
}

'''

####################################################################################################
LIB_MAIN = '''import 'package:flutter/material.dart';
import 'home_page.dart';

void main() {
  runApp(TheApp());
}

class TheApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomePage(),
    );
  }
}

'''

####################################################################################################
TEST_API_TEST_CONTENTS = '''import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  test("Test API", () async {
    final response = await http.get(Uri.parse("http://localhost:5000"));
    expect(response.statusCode, 200);
    expect(response.body, "Hello World!");
  });
}

'''

####################################################################################################
if __name__ == "__main__":

    create_or_replace_txt_file('./lib/main.dart', LIB_MAIN)
    create_or_replace_txt_file('./lib/home_page.dart', LIB_HOME_PAGE_CONTENTS)

    os.mkdir('./flask')
    create_or_replace_txt_file('./flask/app.py', FLASK_APP_PY_CONTENTS)

    create_or_replace_txt_file('./test/api_test.dart', TEST_API_TEST_CONTENTS)

    os.remove('./test/widget_test.dart')

    print(
        '''
        Add the following dependencies to pubspec.yaml:
        http: ^0.13.3
        
        You must have Python along with flask and flask_cors packages installed.        
        ''')
