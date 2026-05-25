from pathlib import Path

import pandas as pd


def main() -> None:
    raw_dir = Path("tests/fixtures/raw")
    processed_dir = Path("tests/fixtures/processed")

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    fixture_path = raw_dir / "Demographic-aspects-2023.xlsx"

    dataframe = pd.DataFrame(
        [
            list(range(11)),
            list(range(11, 22)),
        ],
        columns=[f"Unnamed: {index}" for index in range(11)],
    )

    dataframe.to_excel(fixture_path, index=False)
    print(f"Created fixture: {fixture_path}")


if __name__ == "__main__":
    main()
