from app.quality import run_data_quality_audit


def main() -> None:
    result = run_data_quality_audit()
    print(result)


if __name__ == "__main__":
    main()
