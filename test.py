
import tempfile
tempdir = tempfile.TemporaryDirectory(
    dir='./input'
)
print(tempdir.name)

