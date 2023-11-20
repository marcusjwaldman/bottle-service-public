def split_string(input_string):
    # Split the string into a list using the comma as a delimiter
    try:
        if input_string.strip() == '':
            return []
        result_list = input_string.split(',')
    except:
        raise ValueError(f"Invalid input string: {input_string}")
    result_list = [x.strip() for x in result_list]
    return result_list
