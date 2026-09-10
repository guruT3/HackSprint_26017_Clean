import os
import html
import werkzeug.utils

def sanitize_text(text: str) -> str:
    """Sanitizes user input to prevent XSS attacks."""
    if not text:
        return ""
    return html.escape(str(text).strip())

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_save_image(file_storage, target_directory: str) -> str:
    """Saves user uploaded images safely and returns file basename."""
    if not file_storage or not file_storage.filename:
        return ""
        
    os.makedirs(target_directory, exist_ok=True)
    filename = werkzeug.utils.secure_filename(file_storage.filename)
    unique_prefix = str(int(os.path.getmtime(target_directory) if os.path.exists(target_directory) else 1000))
    saved_filename = f"{unique_prefix}_{filename}"
    filepath = os.path.join(target_directory, saved_filename)
    file_storage.save(filepath)
    return saved_filename
