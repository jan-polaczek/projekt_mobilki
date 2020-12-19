def separate_array_by_key(arr, key, val):
    arr1 = []
    arr2 = []
    for el in arr:
        if el.as_dict()[key] == val:
            arr1.append(el)
        else:
            arr2.append(el)
    return arr1, arr2
