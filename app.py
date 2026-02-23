from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
user = os.getenv('DB_USER', 'rahul')
pw = os.getenv('DB_PASSWORD', 'password')
host = os.getenv('DB_HOST', 'localhost')
name = os.getenv('DB_NAME', 'app_market')

app = Flask(__name__)
# Assemble the URI
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{user}:{pw}@{host}:5432/{name}"



# --- Database Configuration ---
# Format: postgresql://username:password@localhost:port/database_name
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rahul:Jaegar145@127.0.0.1:5432/app_market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class AppEntry(db.Model):
    __tablename__ = 'marketplace_apps'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.JSON)  # Using JSON type for flexible feature storage

# Initialize database tables
with app.app_context():
    db.create_all()

# --- API Operations ---

# CREATE: Add a new app
@app.route('/apps', methods=['POST'])
def add_app():
    data = request.get_json()
    new_app = AppEntry(
        title=data['title'],
        description=data.get('description', ''),
        features=data.get('features', [])
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"message": "App added successfully", "id": new_app.id}), 201

# READ: Search for apps (using ILIKE for Postgres fuzzy matching)
@app.route('/apps/search', methods=['GET'])
def search_apps():
    query = request.args.get('q', '')
    # PostgreSQL ILIKE is case-insensitive
    results = AppEntry.query.filter(AppEntry.title.ilike(f'%{query}%')).all()
    
    output = []
    for app in results:
        output.append({
            "id": app.id,
            "title": app.title,
            "features": app.features
        })
    return jsonify(output)

# UPDATE: Edit app features
@app.route('/apps/<int:id>', methods=['PUT'])
def update_features(id):
    app_record = AppEntry.query.get_or_404(id)
    data = request.get_json()
    
    if 'features' in data:
        app_record.features = data['features']
        db.session.commit()
        return jsonify({"message": "Features updated"})
    return jsonify({"error": "No features provided"}), 400

# DELETE: Remove an app
@app.route('/apps/<int:id>', methods=['DELETE'])
def remove_app(id):
    app_record = AppEntry.query.get_or_404(id)
    db.session.delete(app_record)
    db.session.commit()
    return jsonify({"message": f"App {id} deleted"})

if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000,debug=True)
    app.run(debug=True)
