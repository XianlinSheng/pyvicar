from pathlib import Path


_script_path = Path(__file__).resolve()
projmgr = _script_path.parent
root = projmgr.parent
sims = root / "sims"
stat = root / "stat"

sims.mkdir(parents=True, exist_ok=True)
stat.mkdir(parents=True, exist_ok=True)
