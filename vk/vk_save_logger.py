from functools import wraps


def save_logger(old_function):
    @wraps(old_function)
    def new_function(*args, **kwargs):
        result = old_function(*args, **kwargs)
        with open('../vk_save_logger.json', 'a', encoding='utf-8') as f:
            f.write(result)
        return result
    return new_function
