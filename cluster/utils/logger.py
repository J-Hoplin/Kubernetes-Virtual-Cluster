import datetime

base_context = "Cluster Manager"


def _color_print(message, context, color_code="\033[0m"):
    reset_code = "\033[0m"
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    if context is not None:
        formatted_output = (
            f"{color_code}[{current_time}]{reset_code}[{context}] {message}"
        )
    else:
        formatted_output = f"{color_code}[{current_time}]{reset_code} {message}"

    print(formatted_output)


# Bright green
def log(message, context=base_context):
    _color_print(message, context, "\033[92m")


# Yellow
def warn(message, context=base_context):
    _color_print(message, context, "\033[33m")


# Red
def error(message, context=base_context):
    _color_print(message, context, "\033[31m")


# Bright Magenta
def debug(message, context=base_context):
    _color_print(message, context, "\033[95m")
