from pathlib import Path
from platform import uname

SYSTEM = uname()[0]

METASHAPE_STANDARD_PATHS = [
    r"C:\Program Files\Agisoft",
    r"C:\Program Files (x86)\Agisoft",
    "~/agisoft"
]

def find_agisoft_python(user_path=None):
    # User specified some path. Prefer it over searching.
    if user_path is not None:
        user_path = Path(user_path)

        # Given path is wrong - stop script
        if not user_path.exists():
            raise Exception("Specified `--metashape-path` is not valid path.")

        # Path leads directly to python executable
        if user_path.is_file() and user_path.name == 'python':
            return user_path

        # Path leads to Metashape executable
        elif user_path.is_file() and user_path.stem == 'metashape':
            metashape_python_exe = user_path.parent / "python"
            metashape_python_exe = metashape_python_exe / ("python" + (".exe" if SYSTEM.lower() == 'windows' else ""))
            return metashape_python_exe

        # Path leads to some folder - try to find python inside
        elif user_path.is_dir():
            possible_exes = list(user_path.glob("**/metashape.exe"))

            if len(possible_exes) == 0:
                possible_exes = list(user_path.glob("../**/metashape.exe"))

            if len(possible_exes) != 1:
                raise Exception("Multiple Metashape executables found. Please specify full Python or Metashape "
                                "executable path.")

            metashape_python_exe = possible_exes[0]
            metashape_python_exe = metashape_python_exe.parent / "python"
            metashape_python_exe = metashape_python_exe / ("python" + (".exe" if SYSTEM.lower() == 'windows' else ""))
            return metashape_python_exe

        raise Exception("Invalid `--metashape-path` usage. Please refer to script help.")

    # Try to find metashape automatically
    else:
        # Look in standard paths
        for standard_path in METASHAPE_STANDARD_PATHS:
            possible_exes = list(Path(standard_path).glob("**/metashape.exe"))
            if len(possible_exes) == 1:
                metashape_python_exe = possible_exes[0]
                metashape_python_exe = metashape_python_exe.parent / "python"
                metashape_python_exe = metashape_python_exe / (
                        "python" + (".exe" if SYSTEM.lower() == 'windows' else ""))
                return metashape_python_exe

        raise Exception("We're unable to find Metashape Python interpreter. Please use `--metashape-path` flag and "
                        "specify it.")
