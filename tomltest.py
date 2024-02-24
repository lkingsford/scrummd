import tomllib

with open("test.toml", "rb") as f:
    output = tomllib.load(f)
print(output)
