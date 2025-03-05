from typing import Set, List
from pathlib import Path

class FileExclusions:
    """Handles file and directory exclusions for repository analysis."""
    
    # Common directories to exclude
    EXCLUDED_DIRS = {
        'venv',
        'env',
        '.env',
        'node_modules',
        'dist',
        'build',
        '.git',
        '__pycache__',
        '.pytest_cache',
        '.coverage',
        '.tox',
        '.idea',
        '.vscode',
        '.DS_Store',
        'target',
        '.gradle',
        '.mvn',
        'bower_components',
        'vendor',
        'tmp',
        'temp',
        'logs',
        'coverage',
        '.next',
        '.nuxt',
        '.output',
        '.serverless',
        '.terraform',
        '.vagrant',
        'site-packages',
        'egg-info',
        'build',
        'eggs',
        'parts',
        'bin',
        'var',
        'sdist',
        'develop-eggs',
        'installs',
        'lib',
        'lib64',
        'wheels',
        'share',
        'include',
        'man',
        'doc',
        'docs',
        'test',
        'tests',
        'spec',
        'specs',
        'fixtures',
        'mocks',
        'examples',
        'demos',
        'samples',
    }
    
    # Common files to exclude
    EXCLUDED_FILES = {
        'package-lock.json',
        'yarn.lock',
        'pnpm-lock.yaml',
        'poetry.lock',
        'Cargo.lock',
        'Gemfile.lock',
        'composer.lock',
        'Pipfile.lock',
        'requirements.txt',
        'requirements-dev.txt',
        'setup.cfg',
        'pyproject.toml',
        'package.json',
        'bower.json',
        'composer.json',
        'Cargo.toml',
        'Gemfile',
        'Rakefile',
        'Makefile', 
        '.editorconfig',
        '.eslintrc',
        '.prettierrc',
        '.stylelintrc',
        '.babelrc',
        '.travis.yml',
        '.circleci',
        '.github',
        'LICENSE',
        'CHANGELOG.md',
        'COPYING',
        'COPYING.LESSER',
        'COPYING.MIT',
        'COPYING.Apache-2.0',
        'COPYING.GPL-2',
        'COPYING.GPL-3',
        'COPYING.LGPL-2.1',
        'COPYING.LGPL-3',
        'COPYING.MPL-2.0',
        'COPYING.ISC',
        'COPYING.BSD-2-Clause',
        'COPYING.BSD-3-Clause',
        'COPYING.Zlib',
        'COPYING.Unlicense',
        'COPYING.WTFPL',
        'COPYING.0BSD',
        'COPYING.AFL-3.0',
        'COPYING.Artistic-2.0',
        'COPYING.CC0-1.0',
        'COPYING.CC-BY-3.0',
        'COPYING.CC-BY-SA-3.0',
        'COPYING.CC-BY-NC-3.0',
        'COPYING.CC-BY-NC-SA-3.0',
        'COPYING.CC-BY-ND-3.0',
        'COPYING.CC-BY-NC-ND-3.0',
        'COPYING.CC-BY-4.0',
        'COPYING.CC-BY-SA-4.0',
        'COPYING.CC-BY-NC-4.0',
        'COPYING.CC-BY-NC-SA-4.0',
        'COPYING.CC-BY-ND-4.0',
        'COPYING.CC-BY-NC-ND-4.0',
    }
    
    @classmethod
    def should_exclude(cls, file_path: str) -> bool:
        """Check if a file or directory should be excluded from analysis.
        
        Args:
            file_path: Path to the file or directory
            
        Returns:
            bool: True if the file should be excluded, False otherwise
        """
        path = Path(file_path)
        
        # Check if any part of the path matches excluded directories
        for part in path.parts:
            if part in cls.EXCLUDED_DIRS:
                return True
        
        # Check if the file name matches excluded files
        if path.name in cls.EXCLUDED_FILES:
            return True
        
        # Check for common patterns in file names
        if any(path.name.endswith(ext) for ext in ['.min.js', '.min.css', '.map']):
            return True
        
        return False