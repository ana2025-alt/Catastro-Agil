from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    def get_by_email(self, email: str): pass

    @abstractmethod
    def create_user(self, data: dict): pass

class DocumentRepositoryPort(ABC):
    @abstractmethod
    def upload_file(self, path: str, content: bytes, content_type: str) -> str: pass

    @abstractmethod
    def save_metadata(self, data: dict): pass

    @abstractmethod
    def get_by_user_id(self, user_id: int): pass 