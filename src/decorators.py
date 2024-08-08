def retry(max_attempts):

    def decor(func):
        counter = 1

        def wrapper(*args, **kwargs):
            nonlocal max_attempts
            nonlocal counter
            if max_attempts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as _ex:
                    print(f"{counter} : {_ex}")
                    max_attempts -= 1
                    counter += 1
                    wrapper(*args, **kwargs)
            else:
                raise Exception("All attempts are spent")
        return wrapper
    return decor
