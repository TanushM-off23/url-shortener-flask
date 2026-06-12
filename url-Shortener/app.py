from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)

def generate_code():
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        if not URL.query.filter_by(short_code=code).first():
            return code

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    short_code = generate_code()
    new_url = URL(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({
        'original_url': original_url,
        'short_url': f'http://localhost:5000/{short_code}',
        'short_code': short_code
    }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        url.clicks += 1
        db.session.commit()
        return redirect(url.original_url)
    return jsonify({'error': 'URL not found'}), 404

@app.route('/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return jsonify({
            'original_url': url.original_url,
            'clicks': url.clicks
        })
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)