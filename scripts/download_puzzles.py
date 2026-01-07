"""
Download Lichess puzzle database
"""

import sys
import requests
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings


def download_lichess_database(force: bool = False):
    """
    Download Lichess puzzle database

    Args:
        force: If True, download even if file already exists

    Returns:
        Path to downloaded file
    """
    Settings.ensure_directories()

    url = Settings.LICHESS_DB_URL
    output_path = Settings.LICHESS_CSV_PATH

    # Check if already downloaded
    if output_path.exists() and not force:
        print(f"Database already exists at: {output_path}")
        print(f"File size: {output_path.stat().st_size / (1024*1024):.1f} MB")
        response = input("Download again? (y/n): ")
        if response.lower() != 'y':
            return output_path

    print(f"Downloading Lichess puzzle database...")
    print(f"URL: {url}")
    print(f"Saving to: {output_path}")
    print(f"\nThis will download ~250MB of compressed data.")
    print(f"Please be patient, this may take several minutes...\n")

    try:
        # Stream download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        print(f"\n✓ Download complete!")
        print(f"File saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size / (1024*1024):.1f} MB")

        return output_path

    except requests.RequestException as e:
        print(f"\n✗ Download failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n✗ Download cancelled by user")
        if output_path.exists():
            output_path.unlink()
            print(f"Partial file deleted.")
        sys.exit(1)


def main():
    """Main entry point"""
    force = '--force' in sys.argv or '-f' in sys.argv
    download_lichess_database(force=force)


if __name__ == "__main__":
    main()
