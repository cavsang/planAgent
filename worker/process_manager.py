import subprocess
import sys
import time


WORKERS = [
    "worker.grading_worker",
    "worker.daily_problem_worker",
]


def start_worker(module_name):

    print(f"[MANAGER] Worker 시작: {module_name}")

    return subprocess.Popen([
        sys.executable,
        "-m",
        module_name
    ])


def main():

    processes = {}

    # 모든 Worker 시작
    for worker in WORKERS:
        processes[worker] = start_worker(worker)

    try:

        while True:

            time.sleep(3)

            # Worker 상태 확인
            for worker, process in list(processes.items()):

                exit_code = process.poll()

                if exit_code is not None:

                    print(
                        f"[MANAGER] Worker 종료: "
                        f"{worker} "
                        f"(exit code={exit_code})"
                    )

                    print(
                        f"[MANAGER] 3초 후 재시작: "
                        f"{worker}"
                    )

                    time.sleep(3)

                    processes[worker] = start_worker(worker)

    except KeyboardInterrupt:

        print("[MANAGER] 종료")

        for process in processes.values():
            process.terminate()


if __name__ == "__main__":
    main()