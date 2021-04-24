import json
import facebook

def main():
	token = "EAAF9rRVvT8wBADQZC4IDg04HPEk3cc4nDcRDfqOrCat2WUhDYsZCH3nXkBwWbzcoe1VtH8yzlMLdnBmmZAp9EyJOZBt0i5ZATj6W4pZAI4tQ5pJfBFu4jFSEc2zxXNDpV9ZCA2ue4q9yzAizxv8sIEXPi1F0Po22EU9yJ9XYhxn7L7elwGnIYFkRcBZBasmWD28ZD"
	graph = facebook.GraphAPI(token)
	#fields = ['first_name', 'location{location}','email','link']
	profile = graph.get_object(id='viettan_10161318054535620')	
	#return desired fields
	print(json.dumps(profile, indent=4))

if __name__ == '__main__':
	main()