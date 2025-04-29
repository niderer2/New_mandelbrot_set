import textwrap
from numba import njit, prange
from types import FunctionType
from typing import Callable, Dict
from func_defef import gamma_function, betta_function, octonion_norm, octonion_vector_norm
from func_defef import multiply_octonions, octonion_pow, divide_octonions, make_octonion, octonion_exp, octonion_log, step
from func_defef import octonion_sin, octonion_cos, octonion_tan, octonion_cot, octonion_sec, octonion_csc
from func_defef import octonion_sinh, octonion_cosh, octonion_tanh, octonion_coth, octonion_sech, octonion_csch
from func_defef import octonion_arcsin, octonion_arccos, octonion_arctan, octonion_arccot, octonion_arcsec, octonion_arccsc, octonion_arsinh, octonion_arcosh, octonion_artanh, octonion_arcoth, octonion_arsech, octonion_arcsch
import numpy as np


@njit
def z_index(z, gradient, iteration, max_iterations, scale_type, log_type, escape_radius):
    n_colors = gradient.shape[0]
    

    if scale_type == "linear":
        return  iteration % len(gradient)
    else:
        if iteration <= 0:
            index = 0
        else:
            alpha = np.log(iteration) / np.log(max_iterations) 
            endet = np.log(1 + escape_radius)
            if log_type == "beautiful":
                zet = 1
            else:
                zet = np.log(1 + octonion_norm(z))
            alpha = alpha * endet * zet
            index = alpha * (len(gradient) - 1)
    
    
        return int(index % len(gradient))

def compiledExpression(z_funct, custom_func, scape_condition, funct_once, functions):
    # Словарь с контекстом для функций, которые будут использоваться
    context = {name: func for name, func in functions}
    
    funct_once = textwrap.indent(funct_once.strip(), ' ' * 8)
    custom_func = textwrap.indent(custom_func.strip(), ' ' * 12)
    
    # Создаем строку кода с динамически вычисляемым выражением

    code = f"""
    
import numpy as np
@njit(parallel=True)
def compiled_func(wi, vi, ui, ti, zi, hi, yi, x, max_iterations, gradient, color3, eror_color, scale_type, log_type, if_while, len_colors):
    colors = np.zeros((len(x), 3), dtype=np.uint8)  # Массив для цветов
    for len_x in prange(len(x)):  # Проходим по всем элементам x
        xi = x[len_x]
{funct_once}
        for i in range(max_iterations):
{custom_func}
            z = {z_funct}
                    
            if z is None:
                colors[len_x] = gradient[0]
                break
            elif {scape_condition}:
                colors[len_x] = gradient[z_index(z, gradient, i, max_iterations, scale_type, log_type, {scape_condition.split(' ')[-1]})]
                break
            
        if i == max_iterations - 1:
            colors[len_x] = color3
    return colors
"""
    # Контекст для exec
    exec_context = {'njit': njit}
    exec_context.update(context)

    try:
        # Компиляция и возвращение скомпилированной функции
        exec(code, exec_context)
    except Exception as e:
        print("Ошибка при компиляции сгенерированной функции:")
        print("-------- Сгенерированный код --------")
        print(code)
        print("-------- Конец кода --------")
        raise e  # Пробрасываем исключение дальше для диагностики

    return exec_context['compiled_func']



def cot(vector):
    return 1 / np.tan(vector)

def arccot(vector):
    return np.arctan(1 / vector)

def arccoth(vector):
    return 0.5 * np.log((vector + 1) / (vector - 1))

def coth(vector):
    return np.cosh(vector) / np.sinh(vector)

functions = np.array([
   ('z_index', z_index),  
   ('prange', prange), 
   
   ('n_sin', np.sin), 
   ('n_cos', np.cos),
   ('n_tg', np.tan),
   ('n_ctg', cot),
   ('n_sinh', np.sinh),
   ('n_cosh', np.cosh),
   ('n_tgh', np.tanh),
   ('n_ctgh', coth),
   ('n_sqrt', np.sqrt),
   ('n_exp', np.exp),
   ('n_log', np.log),
   ('n_log10', np.log10),
   ('n_log2', np.log2),
   ('n_arcsin', np.arcsin),
   ('n_arccos', np.arccos),
   ('n_arctg', np.arctan),
   ('n_arcctg', arccot),
   ('n_arcsinh', np.arcsinh),
   ('n_arccosh', np.arccosh),
   ('n_arctgh', np.arctanh),
   ('n_arcctgh', arccoth),
   ('n_gamma', gamma_function), 
   ('n_betta', betta_function), 
   
   ('norm', octonion_norm), 
   ('vector_norm', octonion_vector_norm), 
   ('mult', multiply_octonions), #умножение
   ('pow', octonion_pow), #степень
   ('dell', divide_octonions), #деление
   ('oct', make_octonion), #создать октанион
   ('exp', octonion_exp), #экспонента
   ('log', octonion_log), #логарифм
   ('step', step), #сдвиг
   
   ('sin', octonion_sin),
   ('cos', octonion_cos),
   ('tg', octonion_tan),
   ('ctg', octonion_cot),
   ('sec', octonion_sec),
   ('csc', octonion_csc),
   
   ('sinh', octonion_sinh),
   ('cosh', octonion_cosh),
   ('tgh', octonion_tanh),
   ('ctgh', octonion_coth),
   ('sech', octonion_sech),
   ('csch', octonion_csch), 
   
   ('arcsin', octonion_arcsin), 
   ('arcos', octonion_arccos), 
   ('arctg', octonion_arctan), 
   ('arcctg', octonion_arccot), 
   ('arcsec', octonion_arcsec), 
   ('arccsc', octonion_arccsc), 
   
   ('arsinh', octonion_arsinh), 
   ('arcosh', octonion_arcosh), 
   ('artgh', octonion_artanh), 
   ('arcgh', octonion_arcoth), 
   ('arsech', octonion_arsech), 
   ('arcsch)', octonion_arcsch)
   ])



"""


# Пример проверки:
triple = np.array([1, 2j, 0])
power = 2
res_array = triple_pow(triple, power)
res_complex = complex(1, 2) ** 2

print("Результат в виде массива:", res_array)
print("Результат комплексного возведения:", res_complex)
"""

"""
z = Octonion(1.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0)
c = Octonion(1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
z = z ** 2 + c
print(z)
"""