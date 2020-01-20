from pathlib import Path
import subprocess


def main():
  args = 'docker build -t sticker .'
  subprocess.run(args.split(), cwd=Path(__file__).parent.absolute())


if __name__ == '__main__':
  main()