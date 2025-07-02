from flask import Flask, request, jsonify
from flask_cors import CORS
from tfidf_engine import SearchEngine

app = Flask(__name__)
CORS(app)

search_engine = SearchEngine()

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    difficulty = data.get('difficulty')
    language = data.get('language')
    results = search_engine.search(query, difficulty, language)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)