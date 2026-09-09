import subprocess
import sys
import time


def start_worker():
    print("[MANAGER] Worker 시작")

    return subprocess.Popen([
        sys.executable,
        "-m",
        "worker.grading_worker"
    ])


def main():
    while True:
        process = start_worker()

        exit_code = process.wait()

        print(
            f"[MANAGER] Worker 종료 "
            f"(exit code={exit_code})"
        )

        print("[MANAGER] 3초 후 재시작")
        time.sleep(3)


if __name__ == "__main__":
    main()