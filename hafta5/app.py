from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# Kayıtlı işaretçileri saklamak için basit bir liste
saved_markers = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/markers', methods=['GET'])
def get_markers():
    return jsonify(saved_markers)

@app.route('/api/markers', methods=['POST'])
def add_marker():
    data = request.get_json()
    marker = {
        'id': len(saved_markers) + 1,
        'lat': data.get('lat'),
        'lng': data.get('lng'),
        'title': data.get('title', 'Yeni Konum'),
        'description': data.get('description', ''),
        'color': data.get('color', 'red')
    }
    saved_markers.append(marker)
    return jsonify(marker), 201

@app.route('/api/markers/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    global saved_markers
    saved_markers = [m for m in saved_markers if m['id'] != marker_id]
    return jsonify({'success': True})

@app.route('/api/markers/clear', methods=['DELETE'])
def clear_markers():
    global saved_markers
    saved_markers = []
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)