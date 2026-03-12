#by order of Phillip, a new way to automate the stuff, not involving the asyncio, as simple as possible, must be created. Et viola.

while true; do 
	poetry run greenhouse see-data
	poetry run greenhouse water
