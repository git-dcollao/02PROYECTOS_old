"""
Sistema de Validación y Sanitización de Datos
Clases y decoradores para validar entrada de datos de forma consistente
"""
import re
import html
import bleach
from functools import wraps
from flask import request, jsonify, flash, redirect, url_for
from wtforms import ValidationError
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Clase centralizada para validaciones de datos"""
    
    # Patrones de validación
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    RUT_PATTERN = re.compile(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{8,15}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s]+$')
    
    # Configuración de sanitización HTML
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        if not email or not isinstance(email, str):
            return False, "Email es requerido"
        
        email = email.strip().lower()
        if not DataValidator.EMAIL_PATTERN.match(email):
            return False, "Formato de email inválido"
        
        if len(email) > 254:
            return False, "Email demasiado largo"
            
        return True, email
    
    @staticmethod
    def validate_rut(rut):
        """Validar RUT chileno"""
        if not rut or not isinstance(rut, str):
            return False, "RUT es requerido"
        
        rut = rut.strip().replace(" ", "")
        
        # Agregar puntos y guión si no los tiene
        if not DataValidator.RUT_PATTERN.match(rut):
            # Intentar formatear si solo son números
            if re.match(r'^\d{7,8}[\dkK]$', rut):
                rut_numbers = rut[:-1]
                check_digit = rut[-1]
                formatted_rut = f"{rut_numbers[:-6]}.{rut_numbers[-6:-3]}.{rut_numbers[-3:]}-{check_digit}"
                rut = formatted_rut
            else:
                return False, "Formato de RUT inválido"
        
        # Validar dígito verificador
        rut_numbers = rut.replace(".", "").replace("-", "")[:-1]
        check_digit = rut[-1].upper()
        
        if not DataValidator._validate_rut_check_digit(rut_numbers, check_digit):
            return False, "RUT inválido - dígito verificador incorrecto"
            
        return True, rut
    
    @staticmethod
    def _validate_rut_check_digit(rut_numbers, check_digit):
        """Validar dígito verificador del RUT"""
        try:
            reversed_digits = rut_numbers[::-1]
            factors = [2, 3, 4, 5, 6, 7]
            sum_total = 0
            
            for i, digit in enumerate(reversed_digits):
                factor = factors[i % len(factors)]
                sum_total += int(digit) * factor
            
            remainder = 11 - (sum_total % 11)
            
            if remainder == 11:
                expected_digit = '0'
            elif remainder == 10:
                expected_digit = 'K'
            else:
                expected_digit = str(remainder)
                
            return check_digit == expected_digit
        except:
            return False
    
    @staticmethod
    def validate_phone(phone):
        """Validar número de teléfono"""
        if not phone:
            return True, phone  # Teléfono es opcional
        
        phone = phone.strip()
        if not DataValidator.PHONE_PATTERN.match(phone):
            return False, "Formato de teléfono inválido"
            
        return True, phone
    
    @staticmethod
    def validate_text_length(text, min_length=0, max_length=255, field_name="Campo"):
        """Validar longitud de texto"""
        if not text:
            if min_length > 0:
                return False, f"{field_name} es requerido"
            return True, text
        
        if len(text) < min_length:
            return False, f"{field_name} debe tener al menos {min_length} caracteres"
        
        if len(text) > max_length:
            return False, f"{field_name} no puede exceder {max_length} caracteres"
            
        return True, text
    
    @staticmethod
    def validate_alphanumeric(text, field_name="Campo"):
        """Validar que el texto sea alfanumérico"""
        if not text:
            return True, text
        
        if not DataValidator.ALPHANUMERIC_PATTERN.match(text):
            return False, f"{field_name} solo puede contener letras, números y espacios"
            
        return True, text
    
    @staticmethod
    def sanitize_html(text):
        """Sanitizar HTML para prevenir XSS"""
        if not text:
            return text
        
        # Escapar HTML básico
        text = html.escape(text)
        
        # Permitir solo tags seguros con bleach
        clean_text = bleach.clean(
            text,
            tags=DataValidator.ALLOWED_TAGS,
            attributes=DataValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return clean_text
    
    @staticmethod
    def validate_integer_range(value, min_val=None, max_val=None, field_name="Campo"):
        """Validar rango de enteros"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número entero"
        
        if min_val is not None and int_value < min_val:
            return False, f"{field_name} debe ser mayor o igual a {min_val}"
        
        if max_val is not None and int_value > max_val:
            return False, f"{field_name} debe ser menor o igual a {max_val}"
            
        return True, int_value
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validar que todos los campos requeridos estén presentes"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            
        return True, "OK"

class FormValidator:
    """Validador específico para formularios Flask"""
    
    def __init__(self, request_data):
        self.data = request_data
        self.errors = {}
        self.cleaned_data = {}
    
    def add_validation(self, field_name, validator_func, *args, **kwargs):
        """Agregar validación para un campo"""
        if field_name in self.data:
            is_valid, result = validator_func(self.data[field_name], *args, **kwargs)
            
            if is_valid:
                self.cleaned_data[field_name] = result
            else:
                self.errors[field_name] = result
        else:
            self.errors[field_name] = f"Campo {field_name} es requerido"
    
    def is_valid(self):
        """Verificar si todas las validaciones pasaron"""
        return len(self.errors) == 0
    
    def get_errors(self):
        """Obtener errores de validación"""
        return self.errors
    
    def get_cleaned_data(self):
        """Obtener datos limpios y validados"""
        return self.cleaned_data

def validate_form_data(required_fields=None, optional_fields=None):
    """
    Decorator para validar datos de formulario automáticamente
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear validador
            validator = FormValidator(request.form)
            
            # Validar campos requeridos
            if required_fields:
                for field_config in required_fields:
                    field_name = field_config['name']
                    field_type = field_config.get('type', 'text')
                    field_rules = field_config.get('rules', {})
                    
                    if field_type == 'email':
                        validator.add_validation(field_name, DataValidator.validate_email)
                    elif field_type == 'rut':
                        validator.add_validation(field_name, DataValidator.validate_rut)
                    elif field_type == 'phone':
                        validator.add_validation(field_name, DataValidator.validate_phone)
                    elif field_type == 'text':
                        min_len = field_rules.get('min_length', 0)
                        max_len = field_rules.get('max_length', 255)
                        validator.add_validation(
                            field_name, 
                            DataValidator.validate_text_length,
                            min_len, max_len, field_name
                        )
                    elif field_type == 'integer':
                        min_val = field_rules.get('min_value')
                        max_val = field_rules.get('max_value')
                        validator.add_validation(
                            field_name,
                            DataValidator.validate_integer_range,
                            min_val, max_val, field_name
                        )
            
            # Si hay errores, manejarlos
            if not validator.is_valid():
                errors = validator.get_errors()
                
                # Log de seguridad por datos inválidos
                logger.warning(f"Validation failed for endpoint {request.endpoint}: {errors}")
                
                if request.is_json:
                    return jsonify({'success': False, 'errors': errors}), 400
                else:
                    for error in errors.values():
                        flash(error, 'error')
                    return redirect(request.referrer or url_for('main.dashboard'))
            
            # Pasar datos limpios a la función
            kwargs['validated_data'] = validator.get_cleaned_data()
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

def sanitize_json_input(func):
    """Decorator para sanitizar entrada JSON"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.is_json:
            try:
                json_data = request.get_json()
                if json_data:
                    # Sanitizar recursivamente todos los strings
                    sanitized_data = _sanitize_dict(json_data)
                    request._cached_json = (sanitized_data, True)
            except Exception as e:
                logger.error(f"Error sanitizing JSON input: {e}")
                return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
        
        return func(*args, **kwargs)
    return wrapper

def _sanitize_dict(data):
    """Sanitizar diccionario recursivamente"""
    if isinstance(data, dict):
        return {key: _sanitize_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_sanitize_dict(item) for item in data]
    elif isinstance(data, str):
        return DataValidator.sanitize_html(data)
    else:
        return data