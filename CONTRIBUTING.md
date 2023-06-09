Installation
============

```shell
$ git clone https://github.com/SUSE-Enceladus/csp-billing-adapter-google.git
$ cd csp-billing-adapter-google

# Activate virtual Environment then install
# csp-billing-adapter-google and dev dependences in editable mode
$ pip install -e .[dev]
```

csp-billing-adapter-google is now installed in the active virtual environment in development
mode.

Dev Requirements
================

- bumpversion

Testing Requirements
====================

- coverage
- flake8
- pytest-cov

Contribution Checklist
======================

- All patches must be signed. [Signing Commits](#signing-commits)
- All contributed code must conform to flake8. [Code Style](#code-style)
- All new code contributions must be accompanied by a test.
    - Tests must pass and coverage remain above 90%. [Unit & Integration Tests](#unit-&-integration-tests)
- Follow Semantic Versioning. [Versions & Releases](#versions-&-releases)

Versions & Releases
===================

**csp-billing-adapter-google** adheres to Semantic versioning; see <http://semver.org/> for
details.

[bumpversion](https://pypi.python.org/pypi/bumpversion/) is used for
release version management, and is configured in `setup.cfg`:

```shell
$ bumpversion major|minor|patch
$ git push
```

Bumpversion will create a commit with version updated in all locations.
The annotated tag is created separately.

```shell
$ git tag -a v{version}
# git tag -a v0.0.1

# Create a message with the changes since last release and push tags.
$ git push --tags
```

Unit & Integration Tests
========================

All tests should pass and test coverage should remain above 90%.

The tests and coverage can be run directly via pytest.

```shell
$ pytest --cov=csp_billing_adapter_google
```

Code Style
==========

Source should pass flake8 and pep8 standards.

```shell
$ flake8 csp_billing_adapter_google
```

Signing Commits
===============

The repository and the code base patches sent for inclusion must be GPG
signed. See the GitHub article, [Signing commits using
GPG](https://help.github.com/articles/signing-commits-using-gpg/), for
more information.
