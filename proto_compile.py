import argparse
import fileinput
from subprocess import check_call, CalledProcessError


def compile(path):
    try:
        check_call(
            f"python -m grpc_tools.protoc --proto_path={path} --python_out=app/billing/grpc/pb2"
            f" --python_grpc_out=app/billing/grpc/pb2 {path}/billing.proto",
            shell=True,
            stderr=None,
            stdout=None,
            executable="bash",
        )
    except CalledProcessError as e:
        print(e)

    with fileinput.FileInput("app/billing/grpc/pb2/billing_grpc.py", inplace=True) as file:
        for line in file:
            print(line.replace("import billing_pb2", "from app.billing.grpc.pb2 import billing_pb2"), end="")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", const=1, default=None)
    args = p.parse_args()
    path = args.path
    compile(path)
