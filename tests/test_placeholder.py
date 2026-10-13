import ledger


def test_package_imports() -> None:
    assert ledger.__doc__ is not None
