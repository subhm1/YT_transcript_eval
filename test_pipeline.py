from pipeline import run_pipeline


URL = "https://www.youtube.com/watch?v=3YZ5Nv-q0YI"


if __name__ == "__main__":
    result = run_pipeline(URL)

    print("\nFINAL SUMMARY")
    print("=" * 60)
    print(result["summary"])

    print("\nMETRICS")
    print("=" * 60)

    for name, value in result["metrics"].items():
        print(f"{name}: {value}")