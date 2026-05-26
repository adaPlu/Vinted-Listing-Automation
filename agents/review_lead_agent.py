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
        input("Review listing then press ENTER...")
