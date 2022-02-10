# Methods for iterating in python, Rust-style
```python
# Before:
n = next(enumerate(filter(lambda i: i % 2 == 0, map(lambda i: i * 2, range(10)))))

# After
n = (
    PostIter(range(10))
    .map(lambda i: i * 2)
    .filter(lambda i: i % 2 == 0)
    .enumerate()
    .next()
)
```
