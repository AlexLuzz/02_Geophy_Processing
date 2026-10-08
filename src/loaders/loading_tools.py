from pathlib import Path

def resolve_files(source: Path | str | list, pattern: str = "*") -> list[Path]:
        if isinstance(source, list):
            return [Path(f) for f in source if Path(f).exists()]
        
        source_path = Path(source)
        if source_path.is_file(): return [source_path]
        if source_path.is_dir(): return list(source_path.glob(pattern))
        if source_path.parent.is_dir(): return list(source_path.parent.glob(source_path.name))
        
        raise FileNotFoundError(f"Path does not exist: {source_path}")