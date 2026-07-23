import time
import hashlib
from flask import Flask, request, jsonify
from adapters.supabase_adapter import SupabaseAdapter

app = Flask(__name__)
repo = SupabaseAdapter()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    try:
        usuario = repo.get_by_email(email)
        if usuario:
            return jsonify({"status": "success", "usuario_id": usuario["id"], "nombre": usuario["nombre"]})
        return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/registrar-cliente', methods=['POST'])
def registrar_cliente():
    data = request.json or {}
    try:
        nuevo_usuario = {
            "cedula": data.get('cedula'),
            "nombre": data.get('nombre'),
            "email": data.get('email'),
            "password_hash": "scrypt:32768:8:1$yXpZ...hash_simulado",
            "rol": "cliente"
        }
        res = repo.create_user(nuevo_usuario)
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/subir', methods=['POST'])
def subir_documento():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "Sin archivo"}), 400
            
        archivo = request.files['file']
        usuario_id = int(request.form.get('usuario_id'))
        categoria = request.form.get('categoria')
        
        contenido = archivo.read()
        sha256_hash = hashlib.sha256(contenido).hexdigest()
        nombre_unico = f"{int(time.time())}_{archivo.filename}"
        path = f"{usuario_id}/{nombre_unico}"
        
        url_publica = repo.upload_file(path, contenido, archivo.content_type)
        
        data = {
            "usuario_id": usuario_id, 
            "categoria": categoria, 
            "nombre_archivo": archivo.filename, 
            "url_storage": url_publica, 
            "sha256_hash": sha256_hash
        }
        repo.save_metadata(data)
        return jsonify({"status": "success", "hash": sha256_hash})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/documentos/<int:usuario_id>', methods=['GET'])
def obtener_documentos(usuario_id):
    try:
        documentos = repo.get_by_user_id(usuario_id)
        return jsonify(documentos)
    except Exception as e:
        return jsonify({"error_real": str(e)}), 500 