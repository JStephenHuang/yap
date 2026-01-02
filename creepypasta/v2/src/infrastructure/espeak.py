"""eSpeak NG configuration for phonemizer."""

import os
from pathlib import Path


def configure_espeak() -> None:
    """
    Ensure eSpeak NG library is configured for phonemizer.
    
    Sets the PHONEMIZER_ESPEAK_LIBRARY environment variable if:
    - It's not already set
    - The eSpeak NG DLL exists at the expected location
    
    Raises:
        RuntimeError: If eSpeak NG is not found at the expected location.
    """
    # Check if already configured
    if os.environ.get("PHONEMIZER_ESPEAK_LIBRARY"):
        return
    
    # Default Windows installation path
    espeak_dll_path = Path(r"C:\Program Files\eSpeak NG\libespeak-ng.dll")
    
    if espeak_dll_path.exists():
        # Set the environment variable for this process and child processes
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = str(espeak_dll_path)
        print(f"✓ Configured eSpeak NG: {espeak_dll_path}")
    else:
        raise RuntimeError(
            f"eSpeak NG not found at expected location: {espeak_dll_path}\n"
            "Please install eSpeak NG using: scoop install espeak.espeak-ng\n"
            "Or set PHONEMIZER_ESPEAK_LIBRARY manually to the correct path."
        )
