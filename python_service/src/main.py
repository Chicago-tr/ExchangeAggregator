from spark import run_spark


def main():
    print("==========================================")
    print("Running analysis...")
    print("==========================================")
    run_spark()
    print("==========================================")
    print("Analysis can be viewed with command: 'python3 dashapp.py'")
    print("==========================================")
    return


if __name__ == "__main__":
    main()
