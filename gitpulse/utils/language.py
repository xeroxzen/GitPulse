from typing import Optional
from pathlib import Path
from pygments.lexers import get_lexer_for_filename, get_all_lexers
from pygments.util import ClassNotFound

class LanguageDetector:
    def __init__(self):
        """Initialize the language detector."""
        # Cache for lexer mappings
        self._lexer_cache = {}
        
        # Initialize lexer mappings
        for lexer in get_all_lexers():
            for alias in lexer[1]:
                self._lexer_cache[alias] = lexer[0]
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file path or content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Detected programming language
        """
        try:
            # Try to get lexer from filename
            lexer = get_lexer_for_filename(file_path)
            return lexer.name
        except ClassNotFound:
            # If filename detection fails, try extension-based detection
            return self._detect_from_extension(file_path)
    
    def _detect_from_extension(self, file_path: str) -> str:
        """Detect language from file extension."""
        # Map file extensions to languages
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.hpp': 'C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.kts': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'MATLAB',
            '.sh': 'Shell',
            '.bash': 'Shell',
            '.zsh': 'Shell',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'SASS',
            '.less': 'LESS',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.txt': 'Text',
            '.rst': 'reStructuredText',
            '.tex': 'TeX',
            '.latex': 'LaTeX',
            '.bib': 'BibTeX',
            '.ini': 'INI',
            '.cfg': 'INI',
            '.conf': 'INI',
            '.toml': 'TOML',
            '.csv': 'CSV',
            '.tsv': 'TSV',
            '.diff': 'Diff',
            '.patch': 'Diff',
            '.dockerfile': 'Dockerfile',
            '.dockerignore': 'Dockerfile',
            '.gitignore': 'Git',
            '.env': 'Properties',
            '.properties': 'Properties',
        }
        
        ext = Path(file_path).suffix.lower()
        return extension_map.get(ext, 'Unknown') 