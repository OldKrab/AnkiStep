import argparse
from api.api import AnkiStepAPI

def main(args):
    api = AnkiStepAPI()
    if (
        args.login is None
        and args.password is not None
        or args.login is not None
        and args.password is None
    ):
        print("You need to enter login and password.")
        return

    api.authorize(args.client_id, args.client_secret, args.login, args.password)
    api.load_stepik_course(int(args.quiz_id))
    api.save_quizes_anki()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument(
        "-i", "--client_id", help="Client id of your application", required=True
    )
    parser.add_argument(
        "-s", "--client_secret", help="Client secret of your application", required=True
    )
    parser.add_argument(
        "-q", "--quiz_id", help="Id of Stepik's course to import", required=True
    )
    parser.add_argument("-l", "--login", help="Your Stepik's login", required=False)
    parser.add_argument(
        "-p", "--password", help="Your Stepik's password", required=False
    )
    args = parser.parse_args()

    main(args)
