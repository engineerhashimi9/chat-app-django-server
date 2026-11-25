import requests


data={
    "name":"John Doe",
    "last_name":"Doe",
    "email":"user@example.com",
    "password":"password123"
}
request=requests.post("http://127.0.0.1:8000/api/accounts/register/",data=data)

{
    "name": "newhashimi",
    "last_name": "sadat",
    "email": "hashimi@x.com",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5NjE5ODY3NiwiaWF0IjoxNzk1NTkzODc2LCJqdGkiOiJiNThhNjU1MGE1ODc0MmQ4OWYyYmMyYzhiNzMwYjcwYSIsInVzZXJfaWQiOiI0In0.W8-QtB-Y9sFXHfzIyISYuIqt1MpZd83QrHtMn9AgUeM",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzk1NTk3NDc2LCJpYXQiOjE3OTU1OTM4NzcsImp0aSI6Ijk5M2NjZTZmNDlmNDRjYzRhNDFiNTBiZWM0ZWJkYjEwIiwidXNlcl9pZCI6IjQifQ.1OIQMrQayVpjmZIznlgCHoOf7O3VOB0jK9Bz2vnPMDQ"
}
