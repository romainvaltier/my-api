# My-API helps you do awesome stuff. 🚀

## user

- Only authentified users can get access to the API
- Only **Captain Nemo** can access to create, update and delete endpoints

## categorie

- unicity on id not implemented
- parent as Tree type not implemented and possible solutions are :
  - Treelib : [https://treelib.readthedocs.io/en/latest/](https://treelib.readthedocs.io/en/latest/)
  - AnyTree : [https://github.com/c0fec0de/anytree](https://github.com/c0fec0de/anytree)

## equipement

- unicity on id not implemented
- logic to create equipement not fully integrated with category "model"

## testing

- pytest : [https://docs.pytest.org/en/7.1.x/contents.html](https://docs.pytest.org/en/7.1.x/contents.html)
- 7 tests implemented among at least 20 tests required
- JUnit XML file generated to ease integration to CI

## deployment

- Basic Jenkins files provided for build and deployment
- Docker based

## logging

- not implemented

```python
import logging

 logging.info("my info")
 logging.error("my error")
```

## slug

A slug is a string that can only include characters, numbers, dashes, and underscores. It is the part of a URL that identifies a particular page on a website, in a human-friendly form.

```python
import re

def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '-', s)
  s = re.sub(r'^-+|-+$', '', s)
  return s
```
