import os
import time
import hashlib
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        if len(res.data) > 0:
            usuario = res.data[0]
            return jsonify({"status": "success", "usuario_id": usuario["id"], "nombre": usuario["nombre"]})
        else:
            return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/registrar-cliente', methods=['POST'])
def registrar_cliente():
    data = request.json
    try:
        nuevo_usuario = {
            "cedula": data.get('cedula'),
            "nombre": data.get('nombre'),
            "email": data.get('email'),
            "password_hash": "scrypt:32768:8:1$yXpZ...hash_simulado",
            "rol": "cliente"
        }
        res = supabase.table("usuarios").insert(nuevo_usuario).execute()
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
        
        # AQUÍ ESTÁ LA CORRECCIÓN: Se le dice a Supabase qué tipo de archivo es
        supabase.storage.from_("documentos_catastro").upload(
            path, 
            contenido,
            file_options={"content-type": archivo.content_type}
        )
        
        url_publica = f"{url}/storage/v1/object/public/documentos_catastro/{path}"
        
        data = {
            "usuario_id": usuario_id, 
            "categoria": categoria, 
            "nombre_archivo": archivo.filename, 
            "url_storage": url_publica, 
            "sha256_hash": sha256_hash
        }
        supabase.table("documentos").insert(data).execute()
        return jsonify({"status": "success", "hash": sha256_hash})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/documentos/<int:usuario_id>', methods=['GET'])
def obtener_documentos(usuario_id):
    try:
        respuesta = supabase.table("documentos").select("*").eq("usuario_id", usuario_id).execute()
        return jsonify(respuesta.data)
    except Exception as e:
        return jsonify({"error_real": str(e)}), 500 
