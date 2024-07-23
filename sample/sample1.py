import math
from typing import List


################## custom_types  #######################
# type as class defined
# function direct after the class type.

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


def person_action(person_instance: Person) -> str:
    return f"{person_instance.name} is now performing an action."


class Book:
    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author


def book_action(book_instance: Book) -> str:
    return f"The book '{book_instance.title}' is now open."


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def point_action(point_instance: Point) -> str:
    return f"Moving to point ({point_instance.x}, {point_instance.y})."


class Product:
    def __init__(self, product_id: int, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price


def product_action(product_instance: Product) -> str:
    return f"Product '{product_instance.name}' is ready for use."


def add_book(book: Book, biblio: list) -> None:
    biblio.append(book)


def add_methode1(value_1: int, value_2: int) -> None:
    result = value_1 + value_2
    result += 0


def greet(name: str) -> None:
    """Greets the user."""
    print(f"Hello, {name}!")


###############   custom type 2   #################

class CustomBoolean:
    def __init__(self, value: bool):
        self.value = value

    def __bool__(self):
        return self.value


class CustomString:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class CustomInteger:
    def __init__(self, value: int):
        self.value = value

    def __int__(self):
        return self.value


class CustomFloat:
    def __init__(self, value: float):
        self.value = value

    def __float__(self):
        return self.value


def is_custom_boolean(value: CustomBoolean) -> bool:
    """Checks the boolean value of CustomBoolean."""
    return bool(value)


def custom_string_uppercase(text: CustomString) -> CustomString:
    """Converts a CustomString to uppercase."""
    return CustomString(text.value.upper())


def custom_integer_square(value: CustomInteger) -> CustomInteger:
    """Calculates the square of a CustomInteger."""
    return CustomInteger(value.value ** 2)


def custom_float_round(value: CustomFloat) -> CustomFloat:
    """Rounds the value of a CustomFloat."""
    if isinstance(value.value, float):
        if math.isnan(value.value) or math.isinf(value.value):
            return CustomFloat(value.value)  # Return unchanged for NaN or Infinity
    return CustomFloat(round(value.value))


##########  standard type  #################################


def add_methode(value_1: int, value_2: int) -> int:
    result = value_1 + value_2
    return result


def reverse_string(text: str) -> str:
    """Reverses the order of characters in a string."""
    return text[::-1]


def calculate_area(length: float, width: float) -> float:
    """Calculates the area of a rectangle."""
    return length * width


def is_prime(num: int) -> bool:
    """Checks if a number is prime."""
    if num <= 1:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True


def factorial(num: int) -> int:
    """Calculates the factorial of a non-negative integer."""
    if num < 0:
        return None
    result = 1
    for i in range(1, num + 1):
        result *= i
    return result


def celsius_to_fahrenheit(celsius: float) -> float:
    """Converts temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def is_palindrome(text: str) -> bool:
    """Checks if a string reads the same backward as forward (ignoring case)."""
    text = text.lower().replace(" ", "")
    return text == text[::-1]


def gcd(a: int, b: int) -> int:
    """Calculates the greatest common divisor of two integers."""
    while b != 0:
        a, b = b, a % b
    return a


def is_even(num: int) -> bool:
    """Checks if a number is even (divisible by 2)."""
    return num % 2 == 0


def is_even2(num=2) -> bool:
    """Checks if a number is even (divisible by 2)."""
    return num % 2 == 0

# def mul_by_k(v:float, k=2) -> bool:
#   """Checks if a number is even (divisible by 2)."""
#   return v*k
