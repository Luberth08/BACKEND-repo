from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Mapea client_id (ej. id de usuario conductor o id de taller) al socket activo
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/notificaciones/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Opcionalmente se puede recibir ping para mantener viva la conexion
            # await manager.send_personal_message(f"Ping recibido: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

async def notificar_usuario(client_id: str, mensaje: str):
    """
    Función helper importable para usar desde otros endpoints (e.g. emergencias.py, tecnicos.py)
    """
    await manager.send_personal_message(mensaje, client_id)
