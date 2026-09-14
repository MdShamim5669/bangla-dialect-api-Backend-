import sys

def main():
    print("========================================")
    print(" Hugging Face Login Assistant")
    print("========================================")
    try:
        from huggingface_hub import login
    except ImportError:
        print("Error: huggingface_hub library is not installed.")
        print("Please run: pip install huggingface_hub")
        sys.exit(1)

    print("\nPlease enter your Hugging Face Access Token (get it from https://huggingface.co/settings/tokens):")
    token = input("Token: ").strip()

    if not token:
        print("Token cannot be empty. Exiting.")
        sys.exit(1)

    try:
        login(token=token, add_to_git_credential=True)
        print("\n🎉 Congratulations! Successfully logged into Hugging Face.")
    except Exception as e:
        print(f"\n❌ Login failed: {e}")

if __name__ == "__main__":
    main()
