items = {"SWCFP100106264":{"name":"Watch","price":4000},
		 "SFQDYRHXVGWTJ":{"name":"Apple Pencil","price":8000},
		 "9780241470046":{"name":"The Practice","price":500},
 		 "9781847941831":{"name":"Atomic Habits","price":500},
 		 "1SGY50X88832Z13GRT42":{"name":"Mouse","price":1500},
		 "4005900144652":{"name":"Cream","price":100},
		 "190198648891":{"name":"iPad","price":10000},
		}

total_bill = 0
bill = []

while True:
	print("Scan your BarCode")
	value = input()
	end_code = "9781492090793" 
	if value == end_code:
		print("Shopping Done")
		break

	for key in items.keys():
		if key==value:
			item = items[key]
			print(f"This is:{item['name']}, Price is: {item['price']}")
			total_bill+=item['price']
			bill.append(item)
			break
	else:
		print("Item Not Found",value)

for i,item in enumerate(bill):
	print(f"{i+1}. {item['name']}, {item['price']}")

print(f'\nYour Total Cost is: Rs.{total_bill}')