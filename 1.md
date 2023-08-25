# What is Pylint?

Pylint is a widely used static code analysis tool for Python programming. It assists developers in improving the quality and maintainability of their Python code by analyzing it for potential errors, style inconsistencies, and adherence to coding standards. Pylint evaluates code against a set of predefined rules and conventions, identifying issues such as syntax errors, variable naming inconsistencies, unused variables, and more. It generates detailed reports and provides suggestions for code improvements, helping developers write cleaner, more readable, and efficient Python code. Pylint contributes to better code quality, reduced bugs, and enhanced code maintainability across projects.

When writing Python code for service mapping or other NSO development Pylint is a great tool to use. In the following example you will use it to lint your package code as part of package build process.

## Use Pylint for NSO Python package analysis

You will learn how to use Pylint on an existing NSO package that uses Python to implement mapping logic.

### Modify package Makefile to include pylint

First thing you will do is add recipe to the package Makefile. Open Makefile under `packages/loopback/src/Makefile` and add the the call for `pylint` target to the `all:` target on the first line:  

```Makefile
all: fxs pylint
```

Now add the `pylint` target to the bottom of the `Makefile`, it should look like the following snippet:

```Makefile
pylint:
	pylint --rcfile=.pylintrc ../python/loopback
```

In the pylint target you have specified the .pylintrc file that should be used for linting this package. Generate the rcfile using pylint:

```bash
cd packages/loopback/src/
pylint --generate-rcfile > .pylintrc
```

Build the package using `make all` target, this will also trigger the `pylint` target you added as a dependency:
```
bdolenc@THINKPAD: src$ make all
mkdir -p java/src//
/home/bdolenc/develop/nso/nso_6.1/bin/ncsc  `ls loopback-ann.yang  > /dev/null 2>&1 && echo "-a loopback-ann.yang"` \
              -c -o ../load-dir/loopback.fxs yang/loopback.yang
pylint --rcfile=.pylintrc ../python/loopback
************* Module loopback.loopback
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:1:0: C0114: Missing module docstring (missing-module-docstring)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:6:0: C0115: Missing class docstring (missing-class-docstring)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:16:8: W0622: Redefining built-in 'vars' (redefined-builtin)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:8:4: C0116: Missing function or method docstring (missing-function-docstring)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:9:49: W0212: Access to a protected member _path of a client class (protected-access)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:25:0: C0115: Missing class docstring (missing-class-docstring)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:3:0: C0411: standard import "import ipaddress" should be placed before "import ncs" (wrong-import-order)

------------------------------------------------------------------
Your code has been rated at 6.11/10 (previous run: 6.11/10, +0.00)

make: *** [Makefile:32: pylint] Error 20
```

As you can see pylint detected multiple problems with the loopback package Python code. You will fix some of these problems and change the rcfile to ignore the rest of them.

### Fix problems in Python code

In the printout above you can see that pylint emits different types of messages:

* E: Error - These messages indicate critical issues that are likely to cause problems or errors in your code.
* W: Warning - These messages point out potential issues or code smells that might lead to problems but are not as critical as errors.
* C: Convention - These messages relate to style and coding convention recommendations. They help ensure that your code adheres to a consistent style, making it more readable and maintainable.

You can see that there are no errors detected in the loopback package, so lets first try to fix the warnings. 

The first warning message is:
```
W0622: Redefining built-in 'vars' (redefined-builtin)
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:8:4: C0116:
```

It says that we are using a variable name that is part of Python built-in keywords. You should avoid that to prevent confusion. Pylint also reports filename and the line number where the problem was detected.

Open the file with the problem and rename the problematic variable from `vars` to `tvars`. Your code should look like this:

```python
        tvars = ncs.template.Variables()
        tvars.add('IP_ADDRESS', ip_address)
        template = ncs.template.Template(service)
        template.apply('loopback-template', tvars)
```

Re-run the build of the package. The warning should go away and the score should be higher now.

The next error is about the access to the protected member of a client class - class attributes that starts with the underscore should not be accessed by the user code.
```
/home/bdolenc/develop/nso-labs/labs/good-sw-development-practices/assets/packages/loopback/python/loopback/loopback.py:9:49: W0212: Access to a protected member _path of a client class (protected-access)
```

Let's say you want to make an exception here and keep the access to the `_path` attribute anyway. In this case you can instruct the linter to ignore this line for a specific problem by using the following comment syntax at the end of the problematic line:

```python
        self.log.info('Service create(service=', service._path, ')') # pylint: disable=protected-access
```

Re-run the linter and you will see that now only the convention problems remains. Fix the import ordering problem by placing the import of the ipaddress package before the `import ncs`. The convention is to import Python standard libraries before 3rd party imports.

```python
# -*- mode: python; python-indent: 4 -*-
import ipaddress
import ncs
from ncs.application import Service
```
There are now only documentation related convention messages. In case you want to ignore them package wide you can suppress them by changing the `.pylintrc` file. Open it and find keyword `disable` under MESSAGE CONTROL section. Add the convention messages that are still triggered:
```
disable=raw-checker-failed,
        bad-inline-option,
        locally-disabled,
        file-ignored,
        suppressed-message,
        useless-suppression,
        deprecated-pragma,
        use-symbolic-message-instead,
        C0114,
        C0115,
        C0116
```

Re-run the `make all` command. Now all errors are fixed or suppressed and the build is successful.

```bash
bdolenc@THINKPAD: src$ make all
pylint --rcfile=.pylintrc ../python/loopback

-------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 7.78/10, +2.22)
```