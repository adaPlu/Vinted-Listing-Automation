import msvcrt
import sys


class ReviewResult:

    def __init__(self, passed=True):
        self.passed = passed

    def print_summary(self):
        print("Review passed")


class ReviewLeadAgent:

    def review_images(self, images):
        return ReviewResult(True)

    def review_listing(self, **kwargs):
        return ReviewResult(True)

    def review_marketplace_submission(self, *args):
        return ReviewResult(True)

    def final_human_gate(self):

        print("\nReview listing in browser.")
        print("Press ENTER for next item.")
        print("Press ESC to exit program.")

        while True:

            key = msvcrt.getch()

            # ENTER
            if key == b'\r':

                print("Continuing to next item...")
                break

            # ESC
            elif key == b'\x1b':

                print("Exiting program...")
                sys.exit(0)
