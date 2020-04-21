import hashlib
import json


def test():
    with open('trail.json', 'r', encoding='utf-8') as file:
        form_1 = json.load(file)

    with open('challenge.json', 'r', encoding='utf-8') as file:
        form_2 = json.load(file)

    sig_1 = hashlib.md5()
    sig_2 = hashlib.md5()

    sig_1.update(json.dumps(form_1).encode(encoding='utf-8'))
    sig_2.update(json.dumps(form_2).encode(encoding='utf-8'))

    print('SIG1: ', sig_1.hexdigest())
    print('SIG2: ', sig_2.hexdigest())

    print('---------------------------------------')

    if sig_1.hexdigest() == sig_2.hexdigest():
        print('Challenge Passed!, SIG1 == SIG2')
    else:
        print('Challenge Failed!, SIG1 != SIG2')
        errors = {
            'taskTypeId': None,
            'instJson': None,
            'formJson': None,
            'flowJson': None,
            'flowVerJson': None,
            'formVerJson': None
        }
        for key in errors.keys():
            sig_1 = hashlib.md5()
            sig_2 = hashlib.md5()

            sig_1.update(json.dumps(form_1[key]).encode('utf-8'))
            sig_2.update(json.dumps(form_2[key]).encode('utf-8'))

            if sig_1.hexdigest() != sig_2.hexdigest():
                errors[key] = 1
                print('Error: ', key, ' not mismatch')

    return


if __name__ == "__main__":
    test()
