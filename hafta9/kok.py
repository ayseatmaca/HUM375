import numpy as np
from sympy import symbols, Eq, solve
# 3x^5 + 2x^3 - 5x^2 + 7x - 1
def evaluate_polynomial(coefficients, x):
    result = 0
    for i in range(len(coefficients)):
        result += coefficients[i] * (x ** (len(coefficients) - 1 - i))
    return result

coefficients = [3, 0, 2, -5, 7, -1]

def find_roots(coefficients):
    roots = np.roots(coefficients)
    return roots

roots = find_roots(coefficients)
print(f"Polinomun kökleri: {roots}")

def find_derivative(coefficients):
    derivative_coefficients = []
    degree = len(coefficients) - 1
    for i in range(len(coefficients) - 1):
        derivative_coefficients.append(coefficients[i] * degree)
        degree -= 1
    return derivative_coefficients

derivative_coefficients = find_derivative(coefficients)
print(f"Polinomun türevinin katsayıları: {derivative_coefficients}")

dev_re_coefficients = find_derivative(derivative_coefficients)
print(f"Polinomun ikinci türevinin katsayıları: {dev_re_coefficients}")

integral_coefficients = [0] + [coeff / (i + 1) for i, coeff in enumerate(coefficients)]
print(f"Polinomun integralinin katsayıları: {integral_coefficients}")

belirli_integral = (evaluate_polynomial(integral_coefficients, 2) - evaluate_polynomial(integral_coefficients, 0))
print(f"Polinomun 0 ile 2 arasındaki belirli integrali: {belirli_integral}")

f_x_y = lambda x, y: (3*x**2 + 2*y**2)**4
def evaluate_multivariable_function(func, x, y):
    return func(x, y)
result_multivariable = evaluate_multivariable_function(f_x_y, 1, 2)
print(f"f(1, 2) = {result_multivariable}")

def partial_derivative(func, var='x', h=1e-5):
    if var == 'x':
        return (func(1 + h, 2) - func(1 - h, 2)) / (2 * h)
    elif var == 'y':
        return (func(1, 2 + h) - func(1, 2 - h)) / (2 * h)
    else:
        raise ValueError("Variable must be 'x' or 'y'.")        

partial_x = partial_derivative(f_x_y, var='x')
partial_y = partial_derivative(f_x_y, var='y')  
print(f"f'nin x'e göre kısmi türevi: {partial_x}")
print(f"f'nin y'ye göre kısmi türevi: {partial_y    }")

çift_katlı_integral = lambda x, y: (3*x**2 + 2*y**2)**4
def evaluate_double_integral(func, x_limits, y_limits, num_points=100):
    x_values = np.linspace(x_limits[0], x_limits[1], num_points)
    y_values = np.linspace(y_limits[0], y_limits[1], num_points)
    integral_value = 0
    for x in x_values:
        for y in y_values:
            integral_value += func(x, y)
    return integral_value * (x_limits[1] - x_limits[0]) * (y_limits[1] - y_limits[0]) / (num_points ** 2)

double_integral_value = evaluate_double_integral(çift_katlı_integral, (0, 2), (0, 1), num_points=100)
print(f"Çift katlı integral: {double_integral_value}")
denklem_takımı = ["3*x + 2*y - 5", "2*x - y + 7", "x + 3*y - 1"]
def solve_equations(equations):
    x, y = symbols('x y')
    sympy_equations = []
    for eq in equations:
        sympy_equations.append(Eq(eval(eq), 0))
    solution = solve(sympy_equations, [x, y])
    return solution
solution = solve_equations(denklem_takımı)
print(f"Denklem takımının çözümü: {solution}")
