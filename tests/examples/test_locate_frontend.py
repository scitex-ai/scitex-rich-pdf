from pathlib import Path
from runpy import run_path

from scitex_rich_pdf import get_frontend_package_dir


def test_example_prints_browser_asset_location(capsys):
    # Arrange
    example = Path(__file__).resolve().parents[2] / "examples" / "locate_frontend.py"
    # Act
    run_path(str(example), run_name="__main__")
    # Assert
    assert capsys.readouterr().out.strip() == str(get_frontend_package_dir())
