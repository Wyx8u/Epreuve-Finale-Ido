from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/',methods=['GET'])
def bonjour():
    return "<h1>Bonjour le monde!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)