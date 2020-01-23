from pathlib import Path
import subprocess


def main():
  args = 'python --xml_file=path/to/testxml (and test video)'
  subprocess.run(args.split(), cwd=Path(__file__).parent.absolute())
  # print some success story


if __name__ == '__main__':
  main()