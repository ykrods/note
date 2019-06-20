from coverage import Coverage

cov = Coverage()
cov.start()

from apps.myapp import compare
compare(1,2)
compare(2,1)

cov.stop()

_, executable_lines, missing_lines, _ = cov.analysis("apps/myapp.py")
print("Executable: {}".format(executable_lines))
print("Missing: {}".format(missing_lines))

cov.report()
