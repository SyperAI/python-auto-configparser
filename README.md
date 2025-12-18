# Python auto-configparser
A simple library created to simplify working with configparse in OOP format. This library also supports
automatic creation of a configuration file if it is missing or creation of new fields if they are added.

## How to use?
1. Create section classes which depends on pydantic `BaseModel`:
```python
class TestSection(BaseModel):
    test: str = None
```
> [!WARNING]
> Be sure to specify the default values for the fields!

2. Create config class which depends on `AutoConfig` and contains all sections:
```python
class Config(AutoConfig):
    TEST: TestSection = TestSection()
```

3. Anywhere in your code load your config:
```python
config = Config().load()
```

4. Now you can obtain values from your global config:
```python
test_value = config.TEST.test
```