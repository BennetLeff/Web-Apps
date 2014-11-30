import hmac

SECRET = 278312

def make_secure_value(s):
    return str(s) + "|" + hmac.new(str(s), str(SECRET)).hexdigest()
def check_secure_value(h):
    tohash = h.split("|")
    if (make_secure_value(tohash[0]) == h):
        return tohash[0]
    else:
        return None