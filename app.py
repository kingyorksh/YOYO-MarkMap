# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import models
import os
import json

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///markers.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAPBOX_TOKEN'] = os.getenv('MAPBOX_TOKEN')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo
class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
# Modelo de Usuario----------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader #--------------------------
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route('/')
def index():
    markers = Marker.query.all()
    # Serializar los marcadores en diccionarios
    serialized_markers = [
        {
            'id': marker.id,
            'latitude': marker.latitude,
            'longitude': marker.longitude,
            'title': marker.title,
            'description': marker.description
        }
        for marker in markers
    ]
    return render_template(
        'index.html', 
        mapbox_token=app.config['MAPBOX_TOKEN'],
        markers=serialized_markers
    )


@app.route('/api/markers', methods=['POST'])
def add_marker():
    data = request.json
    new_marker = Marker(
        latitude=data['latitude'],
        longitude=data['longitude'],
        title=data['title'],
        description=data.get('description', '')
    )
    db.session.add(new_marker)
    db.session.commit()
    return jsonify({'id': new_marker.id, 'latitude': new_marker.latitude, 'longitude': new_marker.longitude, 'title': new_marker.title, 'description': new_marker.description}), 201

## RUTA DE MARCADOR 
@app.route('/api/markers', methods=['GET'])
def get_markers():
    markers = Marker.query.all()
    return jsonify([{
        'id': marker.id,
        'latitude': marker.latitude,
        'longitude': marker.longitude,
        'title': marker.title,
        'description': marker.description
    } for marker in markers])
## RUTA DE ELIMNACION
@app.route('/api/markers/<int:marker_id>', methods=['DELETE'])
def delete_marker(marker_id):
    marker = Marker.query.get(marker_id)
    if marker:
        db.session.delete(marker)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Marker not found'}), 404
#*****************************LOGIN**************
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        logout_user()
        flash('¡Registro exitoso! Por favor inicie sesión', 'success')

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/datos')
@login_required
def datos():
    return render_template('datos.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Crear la base de datos
with app.app_context():
    ##db.drop_all()  # Solo si deseas reiniciar la base de datos
    
    db.create_all()
    # Pre-cargar marcadores si la base de datos está vacía
    '''
    if Marker.query.count() == 0:
        initial_markers = [
            Marker(latitude=-1.043161, longitude=-80.456458, title="UTM", description="ubicacion de la universidad tecnica de manabi"),
            Marker(latitude=-1.059811, longitude=-80.449089, title="Parque Las Vegas", description="Descripción del marcador 2"),
        ]
        db.session.bulk_save_objects(initial_markers)
        db.session.commit() '''
    

if __name__ == '__main__':
    app.run(debug=True)