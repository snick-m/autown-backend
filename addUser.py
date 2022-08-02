from ast import arg
import sys
import argparse
from database import createUser

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--Username', help='Username', required=True)
parser.add_argument('-p', '--Password', help='Password', required=True)
parser.add_argument(
    '-t', '--Type', help='User type. 1=Manufacturer, 2=Dealer, 3=user', required=True)
parser.add_argument('-d', '--Data', help='Personal Data')

args = parser.parse_args()

personal_data = {}

for key_value in args.Data.split(','):
    key, value = key_value.split(':')
    personal_data[key] = value

user_doc = createUser(args.Username, int(args.Type), args.Password, personal_data)

if not user_doc or user_doc is None:
    print("User already exists")
else:
    print(f"User created with Address {user_doc['address']}")
