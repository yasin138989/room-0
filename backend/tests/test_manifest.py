from pathlib import Path


def test_project_manifest_exists() -> None:
    assert Path('README.md').exists()
    assert Path('backend').exists()
    assert Path('frontend').exists()
