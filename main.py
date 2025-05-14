from gesture_app import GestureApp

def main():
    app = GestureApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("[INFO] Application stopped by user...")
    except Exception as error:
        print("[ERROR] An error occurred: {}".format(error))
    finally:
        app.cleanup_resources()


if __name__ == "__main__":
    main()
