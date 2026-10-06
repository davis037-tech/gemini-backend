from pathlib import Path 
import uuid 

def safe_filename(name):
    name = Path(name).name
     
    if not name:
      return "unnamed_file.txt"
      
    return name  
      
  
def is_allowed_file(filename):
    allowed_extensions = {
      ".py",
      ".js",
      ".html",
      ".css",
      ".txt",
      ".md",
      ".json"
    }
    extension = Path(filename).suffix.lower()
    return extension in allowed_extensions
    
def save_code(filename, code, generated_dir):
    filename = safe_filename(filename)
    
    if not is_allowed_file(filename):
      return None
      
    file_path =generated_dir / f"{uuid.uuid4().hex}_{filename}" 
    with open(file_path, "w", encoding="utf-8") as file:
      file.write(code)
    
    return file_path
      
      
def extract_code_file(reply):
    return None
      
      
      
      
      
      
      
      