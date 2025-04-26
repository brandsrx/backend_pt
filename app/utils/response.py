class Response:
    """Clase para formatear respuestas JSON"""
    
    @staticmethod
    def success(data=None, message=None, status_code=200):
        """Formato de respuesta exitosa"""
        response = {}
        
        if message:
            response["message"] = message
            
        if data is not None:
            response.update(data if isinstance(data, dict) else {"data": data})
            
        return response, status_code
    
    @staticmethod
    def error(message, status_code=400):
        """Formato de respuesta de error"""
        return {"error": message}, status_code