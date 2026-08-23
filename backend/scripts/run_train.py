from app.train import train_and_register


def main() -> None:
    result = train_and_register()
    print(result)


if __name__ == "__main__":
    main()
