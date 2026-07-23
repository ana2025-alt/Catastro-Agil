import os
from supabase import create_client, Client
from ports.repositories import UserRepositoryPort, DocumentRepositoryPort

class SupabaseAdapter(UserRepositoryPort, DocumentRepositoryPort):
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
        self.bucket = "documentos_catastro"

    def get_by_email(self, email: str):
        res = self.supabase.table("usuarios").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None

    def create_user(self, data: dict):
        return self.supabase.table("usuarios").insert(data).execute()

    def upload_file(self, path: str, content: bytes, content_type: str) -> str:
        self.supabase.storage.from_(self.bucket).upload(
            path, 
            content,
            file_options={"content-type": content_type}
        )
        url = os.environ.get("SUPABASE_URL")
        return f"{url}/storage/v1/object/public/{self.bucket}/{path}"

    def save_metadata(self, data: dict):
        return self.supabase.table("documentos").insert(data).execute()

    def get_by_user_id(self, user_id: int):
        res = self.supabase.table("documentos").select("*").eq("usuario_id", user_id).execute()
        return res.data 