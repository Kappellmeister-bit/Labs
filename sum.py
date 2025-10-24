def add(a: int, b: int) -> int:
    sum = a + b
    return sum

if __name__ == "__main__":
    import sys
    print(add(int(sys.argv[1]), int(sys.argv[2])))
