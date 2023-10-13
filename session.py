import requests

cookies = dict(CMSESSION="eyJpdiI6Im9NWWtobXpxb0hzd1ZvOTRlb3FwNGc9PSIsInZhbHVlIjoiaWxBNmY0VkRNK1p5aWRRZFZRaGM4Vm9mSG50M3N1bDdRbjdjRFpOZ3NDcmZNSmJZdDdUSDUyTC9OQkhDVGsyS3Y2YVVwb0k5dERrQTdOemRnR3FnM1ljYnFwb0w2alVVZlVpSVVJSEtMZEt2ZVZoSSs0S0RqV3NtWjNuZVVmY1UiLCJtYWMiOiI4MWE3MTY3M2YwM2ZiYjJmMDVkOTE3YzczOWI2YzgyM2I3OWM5Y2RmMTEzOGY2MzFlOGQ2MmMzYTkwZTk1NTQ2IiwidGFnIjoiIn0%3D")

for x in range(150):
    incoming = requests.get('http://creativemarket.com/op/download/%s' % x, cookies=cookies)
    if 'content-disposition' not in incoming.headers:
        print ("%s not a valid file" % x)
        continue
    file_name = incoming.headers['content-disposition'].split("\"")[1]
    fsock = open(file_name, 'w')
    fsock.write(incoming.content)
    fsock.close()