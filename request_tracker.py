import time


class RequestTracker:
    def __init__(self, max_retries, max_time):
        self.retries = 0
        self.max_retries = max_retries
        self.max_time = max_time
        self.start_time = time.time()

    def retry(self):
        self.retries += 1

    def should_retry(self):
        if self.retries > self.max_retries:
            print("Max retries reached")
            return False
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.max_time:
            print("Max time reached")
            return False
        return True

    def log_retry(self):
        print(f"Session retry: {self.retries}")
