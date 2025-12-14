import sys
from run import main as run_bot_main

def main():
    # If arguments are provided (other than the script name), run the bot logic.
    # Note: On Windows, double clicking an EXE might pass no args.
    if len(sys.argv) > 1:
        sys.exit(run_bot_main())
    else:
        # Import GUI here to avoid dependencies in CLI mode if possible,
        # and to keep startup fast for the bot process.
        try:
            from gui import MainWindow
            app = MainWindow()
            app.mainloop()
        except ImportError as e:
            print(f"Failed to load GUI: {e}")
            print("Running in console mode...")
            sys.exit(run_bot_main())

if __name__ == "__main__":
    main()
